"""
Django management command to demonstrate invoice trash/restore workflow
Usage: python manage.py test_invoice_workflow
"""

from django.core.management.base import BaseCommand
from sifex_system.models import Masterawb, Invoice
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Test the invoice trash and restore workflow'

    def handle(self, *args, **options):
        
        self.stdout.write('🧪 Testing Invoice Trash/Restore Workflow')
        self.stdout.write('=' * 50)
        
        # Find a sample AWB and invoice for testing
        try:
            sample_invoice = Invoice.objects.filter(deleted=False).first()
            if not sample_invoice:
                self.stdout.write(self.style.WARNING('❌ No active invoices found to test with'))
                return
                
            awb = sample_invoice.awb
            self.stdout.write(f'📋 Testing with Invoice ID: {sample_invoice.id}')
            self.stdout.write(f'📦 Associated AWB: {awb.awb}')
            self.stdout.write(f'💰 Invoice Status: {sample_invoice.status}')
            
            # Show current AWB status
            self.stdout.write(f'\n🔍 Current AWB Status:')
            self.stdout.write(f'   - bill: {awb.bill}')
            self.stdout.write(f'   - invoice_generated: {awb.invoice_generated}')  
            self.stdout.write(f'   - billed: {awb.billed}')
            
            # Simulate deleting invoice
            self.stdout.write(f'\n🗑️  STEP 1: Simulating invoice deletion...')
            original_bill = awb.bill
            original_invoice_generated = awb.invoice_generated  
            original_billed = awb.billed
            
            # Delete logic (as per your delete view)
            sample_invoice.deleted = True
            if awb.billed:
                awb.billed = False
                awb.bill = True
            elif awb.invoice_generated:
                awb.invoice_generated = False
                awb.bill = True
            
            self.stdout.write(f'✅ Invoice marked as deleted')
            self.stdout.write(f'🔄 AWB Status After Delete:')
            self.stdout.write(f'   - bill: {awb.bill}')
            self.stdout.write(f'   - invoice_generated: {awb.invoice_generated}')
            self.stdout.write(f'   - billed: {awb.billed}')
            self.stdout.write(f'📝 AWB is now available for new invoice generation!')
            
            # Simulate restoring invoice  
            self.stdout.write(f'\n♻️  STEP 2: Simulating invoice restore...')
            sample_invoice.deleted = False
            
            # Restore logic (as per your updated restore view)
            if sample_invoice.status == 'paid':
                awb.bill = False
                awb.invoice_generated = False
                awb.billed = True
            elif sample_invoice.status == 'credited':
                awb.bill = False
                awb.invoice_generated = False
                awb.billed = True
            else:
                awb.bill = False
                awb.invoice_generated = True
                awb.billed = False
                
            self.stdout.write(f'✅ Invoice restored to active status')
            self.stdout.write(f'🔄 AWB Status After Restore:')
            self.stdout.write(f'   - bill: {awb.bill}')
            self.stdout.write(f'   - invoice_generated: {awb.invoice_generated}')
            self.stdout.write(f'   - billed: {awb.billed}')
            
            if sample_invoice.status in ['paid', 'credited']:
                self.stdout.write(f'💰 Invoice is {sample_invoice.status} → AWB marked as "billed"')
            else:
                self.stdout.write(f'📄 Invoice is unpaid → AWB marked as "invoice_generated" (prevents duplication)')
            
            # Reset to original state  
            self.stdout.write(f'\n🔄 Resetting to original state...')
            sample_invoice.deleted = False
            awb.bill = original_bill
            awb.invoice_generated = original_invoice_generated
            awb.billed = original_billed
            
            self.stdout.write('\n' + '=' * 50)
            self.stdout.write('✅ Workflow Test Complete!')
            self.stdout.write('\n📋 Summary:')
            self.stdout.write('   1. Delete Invoice → AWB goes to "bill=True" (ready for new invoice)')
            self.stdout.write('   2. Restore Invoice → AWB status depends on payment status:')
            self.stdout.write('      • Paid/Credited → "billed=True" (completed)')  
            self.stdout.write('      • Unpaid → "invoice_generated=True" (prevents duplicates)')
            self.stdout.write('   3. This prevents AWBs from appearing in both lists simultaneously')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error during test: {str(e)}'))
            return