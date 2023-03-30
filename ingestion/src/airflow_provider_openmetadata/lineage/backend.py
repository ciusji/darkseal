#  Copyright 2021 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
OpenMetadata Airflow Lineage Backend
"""

import traceback
from typing import Dict, List, Optional

from airflow.lineage.backend import LineageBackend

from airflow_provider_openmetadata.lineage.config.loader import (
    AirflowLineageConfig,
    get_lineage_config,
)
from airflow_provider_openmetadata.lineage.runner import AirflowLineageRunner
from airflow_provider_openmetadata.lineage.xlets import XLets, get_xlets_from_dag
from metadata.ingestion.ometa.ometa_api import OpenMetadata


# pylint: disable=too-few-public-methods
class OpenMetadataLineageBackend(LineageBackend):
    """
    Sends lineage data from tasks to OpenMetadata.

    Configurable via ``airflow_provider_openmetadata.cfg`` as follows: ::
    [lineage]
    backend = airflow_provider_openmetadata.lineage.OpenMetadataLineageBackend
    airflow_service_name = airflow #make sure this service_name matches
        the one configured in openMetadata
    openmetadata_api_endpoint = http://localhost:8585
    auth_provider_type = no-auth # use google here if you are
        configuring google as SSO
    secret_key = google-client-secret-key # it needs to be configured
        only if you are using google as SSO the one configured in openMetadata
    openmetadata_api_endpoint = http://localhost:8585
    auth_provider_type = no-auth # use google here if you are configuring google as SSO
    secret_key = google-client-secret-key # it needs to be configured
                 only if you are using google as SSO
    """

    def send_lineage(
        self,
        operator: "BaseOperator",
        inlets: Optional[List] = None,
        outlets: Optional[List] = None,
        context: Dict = None,
    ) -> None:
        """
        Send lineage to OpenMetadata

        Args
            operator (BaseOperator):
            inlets (Optional[List]):
            outlets (Optional[List]):
            context (Dict):
        Returns
            None
        """

        try:
            config: AirflowLineageConfig = get_lineage_config()
            metadata = OpenMetadata(config.metadata_config)
            xlets: XLets = get_xlets_from_dag(context["dag"])

            runner = AirflowLineageRunner(
                metadata=metadata,
                service_name=config.airflow_service_name,
                dag=context["dag"],
                xlets=xlets,
                only_keep_dag_lineage=config.only_keep_dag_lineage,
                max_status=config.max_status,
            )
            runner.execute()

        except Exception as exc:  # pylint: disable=broad-except
            operator.log.error(traceback.format_exc())
            operator.log.error(exc)
