"""
dbt-col Core: OpenMetadata ingestion functionality
"""

import os
import sys
from pathlib import Path
from typing import Optional


class DbtColIngestion:
    """Core class for handling dbt to OpenMetadata ingestion"""
    
    def __init__(
        self,
        host_port: str,
        jwt_token: str,
        service_name: str,
        manifest_path: str,
        catalog_path: Optional[str] = None,
        run_results_path: Optional[str] = None
    ):
        self.host_port = host_port
        self.jwt_token = jwt_token
        self.service_name = service_name
        self.manifest_path = manifest_path
        self.catalog_path = catalog_path
        self.run_results_path = run_results_path
        
        # Validate paths
        if not Path(self.manifest_path).exists():
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_path}")
    
    def _create_config(self) -> dict:
        """Create the OpenMetadata workflow configuration"""
        config = {
            'sink': {
                'config': {}, 
                'type': 'metadata-rest'
            },
            'source': {
                'serviceName': self.service_name,
                'sourceConfig': {
                    'config': {
                        'databaseFilterPattern': {
                            'includes': ['.*']
                        },
                        'dbtConfigSource': {
                            'dbtManifestFilePath': self.manifest_path,
                            'dbtConfigType': 'local'
                        },
                        'dbtUpdateDescriptions': True,
                        'dbtUpdateOwners': True,
                        'includeTags': True,
                        'schemaFilterPattern': {
                            'includes': ['.*']
                        },
                        'searchAcrossDatabases': False,
                        'tableFilterPattern': {
                            'includes': ['.*']
                        },
                        'type': 'DBT'
                    }
                },
                'type': 'dbt'
            },
            'workflowConfig': {
                'loggerLevel': 'INFO',
                'openMetadataServerConfig': {
                    'authProvider': 'openmetadata',
                    'hostPort': self.host_port,
                    'securityConfig': {
                        'jwtToken': self.jwt_token
                    }
                }
            }
        }
        
        # Add optional files if they exist
        if self.catalog_path and Path(self.catalog_path).exists():
            config['source']['sourceConfig']['config']['dbtConfigSource']['dbtCatalogFilePath'] = self.catalog_path
        
        if self.run_results_path and Path(self.run_results_path).exists():
            config['source']['sourceConfig']['config']['dbtConfigSource']['dbtRunResultsFilePath'] = self.run_results_path
        
        return config
    
    def run(self) -> bool:
        """Execute the OpenMetadata ingestion workflow"""
        try:
            # Import OpenMetadata workflow
            try:
                from metadata.workflow.metadata import MetadataWorkflow
            except ImportError:
                print("❌ Error: openmetadata-ingestion package not found.")
                print("   Please install it with: pip install openmetadata-ingestion")
                return False
            
            # Create configuration
            config = self._create_config()
            
            # Create workflow instance
            workflow = MetadataWorkflow.create(config)
            
            # Execute the workflow
            workflow.execute()
            workflow.raise_from_status()
            
            # Print the status
            print("📊 Ingestion Summary:")
            workflow.print_status()
            workflow.stop()
            
            return True
            
        except Exception as e:
            print(f"❌ Error during OpenMetadata ingestion: {str(e)}")
            return False


def run_dbt_ingestion_from_config(config: dict) -> bool:
    """
    Legacy function to run ingestion from a config dict
    (for backward compatibility with the original script)
    """
    try:
        from metadata.workflow.metadata import MetadataWorkflow
        
        # Create workflow instance
        workflow = MetadataWorkflow.create(config)
        
        # Execute the workflow
        workflow.execute()
        workflow.raise_from_status()
        
        # Print the status
        print("DBT ingestion completed successfully!")
        workflow.print_status()
        workflow.stop()
        
        return True
        
    except Exception as e:
        print(f"Error during DBT ingestion: {str(e)}")
        return False 