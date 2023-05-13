from dagster import (
    IOManager,
    Definitions,
    build_asset_reconciliation_sensor,
    AssetSelection,
)
from dagster_airbyte import airbyte_resource
from dagchain.loader_logic.base_loaders import save_vectorstore_to_disk


class VectorstoreIOManager(IOManager):
    def load_input(self, context):
        raise NotImplementedError()

    def handle_output(self, context, obj):
        filename = save_vectorstore_to_disk(context.step_key, obj)
        context.add_output_metadata({"filename": filename})

class AirbyteIOManager(IOManager):
    def load_input(self, context):
        print("XXXX")
        print(context.upstream_output.step_context)
        print("XXXX")
        return context.upstream_output.metadata

    def handle_output(self, context, obj):
        raise NotImplementedError()


def DagchainDefinitions(dagchains, additional_assets=[]):
    assets = [
        asset for dagchain in dagchains for asset in dagchain.to_vectorstore_assets()
    ] + additional_assets
    return Definitions(
        assets=assets,
        resources={
            "vectorstore_io_manager": VectorstoreIOManager(),
            "airbyte_io_manager": AirbyteIOManager(),
        },
        sensors=[
            build_asset_reconciliation_sensor(
                AssetSelection.all(),
                name="reconciliation_sensor",
            )
        ],
    )
