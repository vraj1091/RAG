"""
Tally XML over HTTP Integration Service - COMPLETE FILE WITH P&L
Extracts data directly from TallyPrime without exports using XML API
🔥 Multi-company support + Debug logging + P&L Calculation
"""

import requests
from lxml import etree
from typing import Dict, List, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)

class TallyXMLService:
    """Direct Tally integration using XML over HTTP (universal, no ODBC needed)"""
    
    def __init__(self, tally_host: str = "localhost", tally_port: int = 9000):
        """
        Initialize Tally XML service
        
        Args:
            tally_host: Tally server IP/hostname (default: localhost)
            tally_port: Tally HTTP port (default: 9000)
        """
        self.base_url = f"http://{tally_host}:{tally_port}"
        self.timeout = 30  # seconds
        logger.info(f"✅ Tally XML Service initialized: {self.base_url}")
    
    def _clean_xml(self, xml_text: str) -> str:
        """Remove invalid XML characters and handle encoding issues"""
        clean = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', xml_text)
        clean = clean.encode('utf-8', errors='ignore').decode('utf-8')
        return clean
    
    def _parse_amount(self, amount_str: str) -> float:
        """
        Parse Tally amount string to float
        Handles formats like: '100000', '-50000', '1,50,000.00'
        """
        if not amount_str:
            return 0.0
        
        try:
            # Remove commas and whitespace
            clean = str(amount_str).replace(',', '').strip()
            return float(clean)
        except (ValueError, AttributeError):
            return 0.0
    
    # ============================================================================
    # 🔥 GET COMPANIES - FOR GLOBAL MULTI-COMPANY SUPPORT
    # ============================================================================
    
    def get_companies(self) -> Dict[str, Any]:
        """🔥 Fetch all companies loaded in TallyPrime"""
        try:
            xml_request = """<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>CompanyList</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>
            <TDL>
                <TDLMESSAGE>
                    <COLLECTION NAME="CompanyList">
                        <TYPE>Company</TYPE>
                        <FETCH>NAME</FETCH>
                    </COLLECTION>
                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>"""
            
            logger.info(f"🏢 Fetching all companies from Tally")
            
            response = requests.post(
                self.base_url,
                data=xml_request,
                headers={'Content-Type': 'text/xml; charset=utf-8'},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                try:
                    parser = etree.XMLParser(recover=True, encoding='utf-8')
                    root = etree.fromstring(response.content, parser=parser)
                    companies = []
                    
                    for company in root.xpath('.//COMPANY'):
                        name_elem = company.find('NAME')
                        name = name_elem.text.strip() if name_elem is not None and name_elem.text else None
                        if name:
                            companies.append({"name": name})
                    
                    if not companies:
                        for cmp in root.findall('.//REMOTECMPINFO'):
                            name = cmp.findtext('NAME', '').strip()
                            if name:
                                companies.append({"name": name})
                    
                    logger.info(f"✅ Found {len(companies)} companies")
                    
                    return {
                        "status": "success",
                        "companies": companies,
                        "count": len(companies)
                    }
                    
                except (etree.XMLSyntaxError, Exception) as parse_error:
                    logger.error(f"❌ XML Parse Error: {parse_error}")
                    return {
                        "status": "error",
                        "message": f"XML parsing failed: {str(parse_error)}",
                        "companies": []
                    }
            else:
                logger.error(f"❌ HTTP {response.status_code}")
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}",
                    "companies": []
                }
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Connection error: {e}")
            return {
                "status": "error",
                "message": f"Cannot connect to Tally at {self.base_url}",
                "companies": [],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Error fetching companies: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "companies": []
            }
    
    # ============================================================================
    # CONNECTION & STATUS
    # ============================================================================
    
    def test_connection(self) -> Dict[str, Any]:
        """Test if Tally is running and accessible"""
        try:
            xml_request = """<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>CompanyInfo</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>
        </DESC>
    </BODY>
</ENVELOPE>"""
            
            logger.info(f"🔍 Testing Tally connection at {self.base_url}")
            response = requests.post(
                self.base_url,
                data=xml_request,
                headers={'Content-Type': 'text/xml; charset=utf-8'},
                timeout=self.timeout
            )
            
            logger.info(f"📡 Tally response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    clean_xml = self._clean_xml(response.text)
                    parser = etree.XMLParser(recover=True, encoding='utf-8')
                    root = etree.fromstring(clean_xml.encode('utf-8'), parser=parser)
                    
                    error = root.findtext('.//LINEERROR')
                    if error:
                        logger.warning(f"⚠️ Tally error: {error}")
                        return {
                            "status": "connected",
                            "message": "Connected to Tally but got error response",
                            "url": self.base_url
                        }
                    
                    companies = []
                    search_paths = [
                        ('.//COMPANYNAME', 'COMPANYNAME'),
                        ('.//NAME', 'NAME'),
                        ('.//REMOTECMPINFO/NAME', 'REMOTECMPINFO/NAME'),
                        ('.//DSPCOMPANYNAME', 'DSPCOMPANYNAME')
                    ]
                    
                    for path, path_name in search_paths:
                        elements = root.findall(path)
                        for elem in elements:
                            if elem.text and elem.text.strip() and len(elem.text.strip()) > 2:
                                company_name = elem.text.strip()
                                if company_name not in companies:
                                    companies.append(company_name)
                                    logger.info(f"✅ Found company via {path_name}: {company_name}")
                        if companies:
                            break
                    
                    if not companies:
                        logger.warning("⚠️ No company name detected")
                        return {
                            "status": "connected",
                            "message": "Connected to Tally - company open but name not detected",
                            "url": self.base_url,
                            "company": "Unknown"
                        }
                    
                    logger.info(f"✅ Successfully connected with {len(companies)} company(ies)")
                    
                    return {
                        "status": "connected",
                        "message": "Successfully connected to Tally",
                        "url": self.base_url,
                        "company": companies[0],
                        "companies": companies,
                        "company_count": len(companies)
                    }
                    
                except (etree.XMLSyntaxError, Exception) as e:
                    logger.error(f"❌ XML parsing error: {e}")
                    return {
                        "status": "connected",
                        "message": "Connected but XML parsing failed",
                        "url": self.base_url,
                        "company": "Unknown",
                        "error": str(e)
                    }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Connection error: {e}")
            return {
                "status": "disconnected",
                "message": f"Cannot connect to Tally at {self.base_url}",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }
    
    # ============================================================================
    # DATA RETRIEVAL METHODS
    # ============================================================================
    
    def get_ledgers(self, company_name: Optional[str] = None) -> Dict[str, Any]:
        """Fetch all ledgers from Tally"""
        try:
            xml_request = """<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>AllLedgers</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>
            <TDL>
                <TDLMESSAGE>
                    <COLLECTION NAME="AllLedgers">
                        <TYPE>Ledger</TYPE>
                        <FETCH>Name, Parent, OpeningBalance, ClosingBalance</FETCH>
                    </COLLECTION>
                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>"""
            
            logger.info(f"📊 Fetching ledgers from active company")
            
            response = requests.post(
                self.base_url,
                data=xml_request,
                headers={'Content-Type': 'text/xml; charset=utf-8'},
                timeout=self.timeout
            )
            
            logger.info(f"📄 HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    parser = etree.XMLParser(recover=True, encoding='utf-8')
                    root = etree.fromstring(response.content, parser=parser)
                    ledgers = []
                    
                    for ledger in root.xpath('.//LEDGER'):
                        name_elem = ledger.find('NAME') or ledger.find('.//NAME')
                        name = name_elem.text.strip() if name_elem is not None and name_elem.text else ''
                        
                        if name:
                            parent_elem = ledger.find('PARENT')
                            opening_elem = ledger.find('OPENINGBALANCE')
                            closing_elem = ledger.find('CLOSINGBALANCE')
                            
                            ledgers.append({
                                'name': name,
                                'parent': parent_elem.text.strip() if parent_elem is not None and parent_elem.text else '',
                                'opening_balance': opening_elem.text if opening_elem is not None and opening_elem.text else '0',
                                'closing_balance': closing_elem.text if closing_elem is not None and closing_elem.text else '0',
                            })
                    
                    logger.info(f"✅ Retrieved {len(ledgers)} ledgers")
                    
                    return {
                        "status": "success",
                        "ledgers": ledgers,
                        "count": len(ledgers),
                        "company": company_name or "Current Company"
                    }
                except Exception as parse_error:
                    logger.error(f"❌ XML Parse Error: {parse_error}")
                    return {
                        "status": "error",
                        "message": f"XML parsing failed: {str(parse_error)}"
                    }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error fetching ledgers: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_vouchers(self, from_date: Optional[str] = None, to_date: Optional[str] = None,
                     voucher_type: Optional[str] = None, company_name: Optional[str] = None) -> Dict[str, Any]:
        """Fetch vouchers from Tally"""
        try:
            date_filter = ""
            if from_date and to_date:
                date_filter = f"<SVFROMDATE>{from_date}</SVFROMDATE><SVTODATE>{to_date}</SVTODATE>"
            
            xml_request = f"""<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>VoucherCollection</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                {date_filter}
            </STATICVARIABLES>
            <TDL>
                <TDLMESSAGE>
                    <COLLECTION NAME="VoucherCollection">
                        <TYPE>Voucher</TYPE>
                        <FETCH>DATE, VOUCHERTYPENAME, VOUCHERNUMBER, PARTYLEDGERNAME, REFERENCE, NARRATION, AMOUNT</FETCH>
                    </COLLECTION>
                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>"""
            
            logger.info(f"📝 Fetching vouchers (type: {voucher_type or 'all'})")
            
            response = requests.post(
                self.base_url,
                data=xml_request,
                headers={'Content-Type': 'text/xml; charset=utf-8'},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                try:
                    parser = etree.XMLParser(recover=True, encoding='utf-8')
                    root = etree.fromstring(response.content, parser=parser)
                    vouchers = []
                    
                    for voucher in root.xpath('.//VOUCHER'):
                        vouchers.append({
                            'date': voucher.findtext('DATE', ''),
                            'voucher_type': voucher.findtext('VOUCHERTYPENAME', ''),
                            'voucher_number': voucher.findtext('VOUCHERNUMBER', ''),
                            'party': voucher.findtext('PARTYLEDGERNAME', ''),
                            'reference': voucher.findtext('REFERENCE', ''),
                            'narration': voucher.findtext('NARRATION', ''),
                            'amount': voucher.findtext('AMOUNT', '0'),
                        })
                    
                    logger.info(f"✅ Retrieved {len(vouchers)} vouchers")
                    
                    return {
                        "status": "success",
                        "vouchers": vouchers,
                        "count": len(vouchers)
                    }
                except (etree.XMLSyntaxError, Exception) as parse_error:
                    logger.error(f"❌ XML Parse Error: {parse_error}")
                    return {
                        "status": "error",
                        "message": f"XML parsing failed: {str(parse_error)}"
                    }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error fetching vouchers: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }
    
    # ============================================================================
    # 🔥 NEW: PROFIT & LOSS CALCULATION FROM LEDGERS
    # ============================================================================
    
    def get_profit_loss_summary(self, from_date: str = "20250401", to_date: str = "20260331") -> Dict[str, Any]:
        """
        🔥 Calculate Revenue, Expenses, and Profit from ledgers
        Returns dashboard-ready data
        """
        try:
            logger.info(f"💰 Calculating P&L summary from {from_date} to {to_date}")
            
            # Get all ledgers with closing balances
            ledgers_result = self.get_ledgers()
            
            if ledgers_result['status'] != 'success':
                return {
                    'status': 'error',
                    'message': 'Failed to fetch ledgers',
                    'revenue': 0,
                    'expenses': 0,
                    'profit': 0
                }
            
            ledgers = ledgers_result['ledgers']
            
            revenue = 0.0
            expenses = 0.0
            
            # Revenue groups (Income side)
            revenue_groups = ['sales accounts', 'direct income', 'indirect income', 'income', 'revenue']
            
            # Expense groups (Expense side)
            expense_groups = ['purchase accounts', 'direct expenses', 'indirect expenses', 'expenses']
            
            for ledger in ledgers:
                parent = ledger.get('parent', '').lower()
                closing = self._parse_amount(ledger.get('closing_balance', 0))
                
                # Check if it's a revenue ledger
                if any(rev_group in parent for rev_group in revenue_groups):
                    revenue += abs(closing)
                    logger.debug(f"Revenue: {ledger['name']} = {closing}")
                
                # Check if it's an expense ledger
                elif any(exp_group in parent for exp_group in expense_groups):
                    expenses += abs(closing)
                    logger.debug(f"Expense: {ledger['name']} = {closing}")
            
            profit = revenue - expenses
            
            logger.info(f"✅ P&L Summary: Revenue=₹{revenue:,.2f}, Expenses=₹{expenses:,.2f}, Profit=₹{profit:,.2f}")
            
            return {
                'status': 'success',
                'revenue': round(revenue, 2),
                'expenses': round(expenses, 2),
                'profit': round(profit, 2),
                'period': f"{from_date} to {to_date}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating P&L: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e),
                'revenue': 0,
                'expenses': 0,
                'profit': 0
            }
    
    def get_stock_items(self, company_name: Optional[str] = None) -> Dict[str, Any]:
        """Fetch all stock items from Tally"""
        try:
            xml_request = """<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Collection</TYPE>
        <ID>StockItemCollection</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>
            <TDL>
                <TDLMESSAGE>
                    <COLLECTION NAME="StockItemCollection">
                        <TYPE>StockItem</TYPE>
                        <FETCH>NAME, PARENT, CATEGORY, OPENINGBALANCE, CLOSINGBALANCE</FETCH>
                    </COLLECTION>
                </TDLMESSAGE>
            </TDL>
        </DESC>
    </BODY>
</ENVELOPE>"""
            
            logger.info(f"📦 Fetching stock items")
            
            response = requests.post(
                self.base_url,
                data=xml_request,
                headers={'Content-Type': 'text/xml; charset=utf-8'},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                try:
                    parser = etree.XMLParser(recover=True, encoding='utf-8')
                    root = etree.fromstring(response.content, parser=parser)
                    items = []
                    
                    for item in root.xpath('.//STOCKITEM'):
                        name_elem = item.find('NAME')
                        name = name_elem.text.strip() if name_elem is not None and name_elem.text else ''
                        if name:
                            parent_elem = item.find('PARENT')
                            category_elem = item.find('CATEGORY')
                            opening_elem = item.find('OPENINGBALANCE')
                            closing_elem = item.find('CLOSINGBALANCE')
                            
                            items.append({
                                'name': name,
                                'parent': parent_elem.text.strip() if parent_elem is not None and parent_elem.text else '',
                                'category': category_elem.text.strip() if category_elem is not None and category_elem.text else '',
                                'opening_balance': opening_elem.text if opening_elem is not None and opening_elem.text else '0',
                                'closing_balance': closing_elem.text if closing_elem is not None and closing_elem.text else '0',
                            })
                    
                    logger.info(f"✅ Retrieved {len(items)} stock items")
                    
                    return {
                        "status": "success",
                        "stock_items": items,
                        "count": len(items),
                        "company": company_name or "Current Company"
                    }
                except (etree.XMLSyntaxError, Exception) as parse_error:
                    logger.error(f"❌ XML Parse Error: {parse_error}")
                    return {
                        "status": "error",
                        "message": f"XML parsing failed: {str(parse_error)}"
                    }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Error fetching stock items: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }


# Global instance
tally_xml_service = TallyXMLService()
