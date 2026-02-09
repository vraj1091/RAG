"""
Tally Knowledge Base Auto-Sync Service
Automatically syncs Tally data to knowledge base and manages updates
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from app.services.tally_xml_service import tally_xml_service
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)

class TallyKBSyncService:
    """Auto-sync Tally data to knowledge base with smart updates"""
    
    def __init__(self):
        self.kb_folder = "uploads/tally_data"
        self.doc_service = DocumentService()
        Path(self.kb_folder).mkdir(parents=True, exist_ok=True)
        logger.info("✅ Tally KB Sync Service initialized")
    
    def sync_tally_to_kb(self, user_id: int, company_name: Optional[str] = None) -> Dict[str, Any]:
        """
        🔥 Main sync function: Fetch Tally data → Convert to JSON → Store in KB
        
        Automatically:
        1. Fetches ledgers, vouchers, stock from Tally
        2. Converts to structured JSON
        3. Deletes old Tally files for this user
        4. Uploads new file to knowledge base
        """
        try:
            logger.info(f"🔄 Starting Tally KB sync for user {user_id}")
            
            # 1. Fetch ALL Tally data
            ledgers_result = tally_xml_service.get_ledgers(company_name)
            vouchers_result = tally_xml_service.get_vouchers(company_name=company_name)
            stock_result = tally_xml_service.get_stock_items(company_name)
            
            if ledgers_result['status'] != 'success':
                return {"status": "error", "message": "Failed to fetch Tally data"}
            
            # 2. Build comprehensive Tally data structure
            tally_data = {
                "company_name": company_name or "Current Company",
                "sync_timestamp": datetime.now().isoformat(),
                "ledgers": ledgers_result.get('ledgers', []),
                "vouchers": vouchers_result.get('vouchers', []),
                "stock_items": stock_result.get('stock_items', []),
                "summary": {
                    "total_ledgers": len(ledgers_result.get('ledgers', [])),
                    "total_vouchers": len(vouchers_result.get('vouchers', [])),
                    "total_stock_items": len(stock_result.get('stock_items', []))
                }
            }
            
            # 3. Convert to searchable text format (for RAG)
            text_content = self._convert_to_text(tally_data)
            
            # 4. Delete old Tally files for this user
            self._delete_old_tally_files(user_id)
            
            # 5. Save new file
            filename = f"tally_data_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(self.kb_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            # 6. Upload to knowledge base database
            doc_result = self.doc_service.upload_document(
                user_id=user_id,
                file_path=filepath,
                filename=filename,
                file_type="tally_data"
            )
            
            logger.info(f"✅ Tally data synced to KB: {filename}")
            
            return {
                "status": "success",
                "message": "Tally data synced to knowledge base",
                "filename": filename,
                "summary": tally_data['summary'],
                "document_id": doc_result.get('id')
            }
            
        except Exception as e:
            logger.error(f"❌ Tally KB sync failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    def _convert_to_text(self, tally_data: Dict[str, Any]) -> str:
        """Convert Tally data to searchable text format"""
        
        lines = []
        lines.append(f"=== TALLY DATA: {tally_data['company_name']} ===")
        lines.append(f"Last Updated: {tally_data['sync_timestamp']}\n")
        
        # Ledgers section
        lines.append("=== LEDGERS ===")
        for ledger in tally_data['ledgers']:
            lines.append(f"Ledger: {ledger['name']}")
            lines.append(f"  Group: {ledger.get('parent', 'N/A')}")
            lines.append(f"  Opening Balance: {ledger.get('opening_balance', '0')}")
            lines.append(f"  Closing Balance: {ledger.get('closing_balance', '0')}")
            lines.append("")
        
        # Vouchers section
        lines.append("\n=== VOUCHERS ===")
        for voucher in tally_data['vouchers']:
            lines.append(f"Voucher: {voucher.get('voucher_number', 'N/A')}")
            lines.append(f"  Date: {voucher.get('date', 'N/A')}")
            lines.append(f"  Type: {voucher.get('voucher_type', 'N/A')}")
            lines.append(f"  Amount: {voucher.get('amount', '0')}")
            lines.append(f"  Narration: {voucher.get('narration', 'N/A')}")
            lines.append("")
        
        # Stock items section
        lines.append("\n=== STOCK ITEMS ===")
        for item in tally_data['stock_items']:
            lines.append(f"Item: {item['name']}")
            lines.append(f"  Category: {item.get('parent', 'N/A')}")
            lines.append(f"  Opening Stock: {item.get('opening_balance', '0')}")
            lines.append(f"  Closing Stock: {item.get('closing_balance', '0')}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _delete_old_tally_files(self, user_id: int):
        """Delete old Tally data files for this user from KB"""
        try:
            # Query database for old Tally files
            old_files = self.doc_service.get_user_documents(user_id, file_type="tally_data")
            
            for doc in old_files:
                logger.info(f"🗑️ Deleting old Tally file: {doc['filename']}")
                self.doc_service.delete_document(doc['id'], user_id)
            
            logger.info(f"✅ Deleted {len(old_files)} old Tally files")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not delete old files: {e}")


# Global instance
tally_kb_sync = TallyKBSyncService()
