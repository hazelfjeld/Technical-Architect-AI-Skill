class InvoiceWorker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, store, provider, events):
        self.store = store
        self.provider = provider
        self.events = events
        self.seen = set()

    def handle(self, invoice):
        invoice_id = invoice['id']
        if invoice_id in self.seen:
            return

        for attempt in range(3):
            try:
                receipt = self.provider.charge(
                    invoice['customer'], invoice['amount_cents']
                )
                break
            except TimeoutError:
                if attempt == 2:
                    raise

        self.store.mark_paid(invoice_id, receipt['id'])
        self.events.publish('invoice.paid', {
            'invoice_id': invoice_id, 'receipt_id': receipt['id']
        })
        self.seen.add(invoice_id)
