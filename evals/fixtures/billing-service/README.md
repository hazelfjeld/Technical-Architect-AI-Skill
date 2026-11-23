# Invoice service proposal

We plan to run eight worker processes. Each receives an invoice message from a queue that may redeliver messages after a worker exits or after an acknowledgment is lost.

An invoice should cause at most one successful charge. After charging, downstream fulfillment needs a payment event. The provider may complete a charge before the caller receives a timeout. It supports a caller-supplied `operation_key`; repeated identical requests with the same key return the original result for 48 hours. Reusing a key with different input is rejected. There is no production system connected to this fixture.

The repository is a design sketch. `storage.py` describes the local persistence contract. The current proposal in `billing.py` uses a singleton to avoid duplicate work. Review the proposal and give the first implementation slices; do not modify the files.
