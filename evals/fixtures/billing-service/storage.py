class InvoiceStore:
    """Persistence sketch. Each call commits independently.

    mark_paid overwrites the invoice status and provider receipt identifier.
    No operation record, deduplication record, or pending-event record exists.
    """

    def __init__(self, database):
        self.database = database

    def mark_paid(self, invoice_id, receipt_id):
        self.database.execute(
            'UPDATE invoices SET status = ?, receipt_id = ? WHERE id = ?',
            ('paid', receipt_id, invoice_id),
        )
        self.database.commit()
