from io import StringIO

import pandas as pd
from pandas import DatetimeIndex

from ...api._examples import _api_history_entity
from ...tests.api import _asserts, _fixtures


def _expected_entity(benchmark_result):
    return _api_history_entity(
        benchmark_result.id,
        benchmark_result.case_id,
        benchmark_result.context_id,
        benchmark_result.run.name,
    )


class TestHistoryGet(_asserts.GetEnforcer):
    url = "/api/history/{}/"
    public = True

    def _create(self):
        return _fixtures.benchmark_result()

    def test_get_history(self, client):
        self.authenticate(client)
        benchmark_result = self._create()
        response = client.get(f"/api/history/{benchmark_result.id}/")
        assert response.status_code == 200
        hist_endpont_resp_deser = response.json
        expected_resp_deser = _expected_entity(benchmark_result)
        assert hist_endpont_resp_deser == expected_resp_deser

    def test_csv_download(self, client):
        self.authenticate(client)
        benchmark_result = self._create()
        response = client.get(f"/api/history/download/{benchmark_result.id}/")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
        assert "filename=" in response.headers["Content-Disposition"]

        df = pd.read_csv(
            StringIO(response.text),
            comment="#",
            index_col="commit_time",
            parse_dates=True,
        )
        assert "svs" in df
        assert isinstance(df.index, DatetimeIndex)
