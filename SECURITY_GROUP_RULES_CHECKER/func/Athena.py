class Athena:
    def __init__(self, athena, wg):
        self.athena = athena
        self.wg = wg

    def is_table_exists(self, table):
        res = self.athena.list_table_metadata(
            CatalogName="AwsDataCatalog", DatabaseName="default"
        )["TableMetadataList"]

        for r in res:
            if r["Name"] == table:
                return True

        return False

    def run_query(self, query):
        return self.athena.start_query_execution(QueryString=query, WorkGroup=self.wg)
