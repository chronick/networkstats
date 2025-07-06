import polars as pl
import json
from io import BytesIO

class ExportManager:
    """Handle data and chart exports."""
    EXPORT_FORMATS = ['PDF', 'PNG', 'CSV', 'Excel', 'JSON']

    def __init__(self, data_source):
        self.data_source = data_source

    async def export_data(self, format: str, timeframe: int, options: dict):
        df = self.data_source.get_export_data(timeframe, options)
        if format == 'CSV':
            return self._export_csv(df)
        elif format == 'Excel':
            return self._export_excel(df)
        elif format == 'JSON':
            return self._export_json(df)
        elif format in ['PDF', 'PNG']:
            return await self._export_chart(df, format)
        else:
            raise ValueError(f"Unknown export format: {format}")

    def _export_csv(self, df: pl.DataFrame) -> bytes:
        return df.write_csv().encode('utf-8')

    def _export_excel(self, df: pl.DataFrame) -> bytes:
        import xlsxwriter
        output = BytesIO()
        with xlsxwriter.Workbook(output) as workbook:
            sheet = workbook.add_worksheet('Data')
            for col, name in enumerate(df.columns):
                sheet.write(0, col, name)
                for row, value in enumerate(df[name].to_list(), start=1):
                    sheet.write(row, col, value)
        return output.getvalue()

    def _export_json(self, df: pl.DataFrame) -> bytes:
        return json.dumps(df.to_dict(as_series=False)).encode('utf-8')

    async def _export_chart(self, df: pl.DataFrame, format: str) -> bytes:
        # Placeholder for actual chart/image export logic
        # In real implementation, generate chart and convert to image/PDF
        if format == 'PDF':
            return b'PDFDATA'
        else:
            return b'IMAGEDATA' 