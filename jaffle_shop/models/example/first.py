# write me a python script that will print "hello world" and use dbt python
import logging
import snowflake.snowpark.functions as F
from snowflake.snowpark.functions import col, upper

def model(dbt, session):
    dbt.config(
        materialized="table",
        alias="sample_table_upper_python"
    )
    
    # Print hello world (note: this will appear in platform logs, not dbt logs)
    print("Hello World from dbt Python model!")
    
    sample_table = dbt.ref("sample_table")
    final_df = sample_table.select("*", upper(col("name")).alias("name_upper_python"))
    
    # Get the log messages from test function
    log_messages = test()
    print(log_messages)
    logging.error(log_messages)
    logging.info(log_messages)
    logging.warning(log_messages)
    logging.debug(log_messages) 
    logging.critical(log_messages)
    logging.exception(log_messages)
    
    # raise Exception(log_messages)
    
    
    # Return the log messages for debugging instead of the dataframe
    # Convert list to a single string for easier reading
    return final_df

def test():
    print("INSIDE TEST FUNCTION")
    import sys
    sys.stdout.flush()
    
    # Create a list to store all log messages
    log_messages = []
    
    """Handle the auto-ingest command logic"""
    import os
    import yaml
    from pathlib import Path
    from typing import Dict, Optional
    
    # Snowflake-friendly logging function that collects messages
    def sf_log(message):
        log_messages.append(f"[DBT-COL] {message}")
        print(f"[DBT-COL] {message}")
        sys.stdout.flush()
    
    sf_log("Starting dbt-col auto-ingestion process...")
    
    def find_dbt_project(start_path: Optional[Path] = None) -> Optional[Path]:
        """Find dbt_project.yml in current directory or parent directories"""
        sf_log("Looking for dbt_project.yml...")
        current = start_path or Path.cwd()
        sf_log(f"Current working directory: {current}")
        
        for path in [current] + list(current.parents):
            dbt_project = path / "dbt_project.yml"
            sf_log(f"Checking path: {path}")
            if dbt_project.exists():
                sf_log(f"Found dbt_project.yml at: {path}")
                return path
        sf_log("dbt_project.yml not found in any parent directories")
        return None

    def load_dbt_project_config(project_dir: Path) -> Dict:
        """Load dbt_project.yml configuration"""
        sf_log(f"Loading dbt project config from: {project_dir}")
        dbt_project_path = project_dir / "dbt_project.yml"
        try:
            with open(dbt_project_path, 'r') as f:
                config = yaml.safe_load(f)
                sf_log("Successfully loaded dbt_project.yml")
                return config
        except Exception as e:
            sf_log(f"Error loading dbt_project.yml: {str(e)}")
            raise

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
            sf_log(f"Initializing DbtColIngestion with service: {service_name}")
            self.host_port = host_port
            self.jwt_token = jwt_token
            self.service_name = service_name
            self.manifest_path = manifest_path
            self.catalog_path = catalog_path
            self.run_results_path = run_results_path
            
            # Validate paths
            if not Path(self.manifest_path).exists():
                sf_log(f"ERROR: Manifest file not found: {self.manifest_path}")
                raise FileNotFoundError(f"Manifest file not found: {self.manifest_path}")
            sf_log(f"Manifest path validated: {self.manifest_path}")
        
        def _create_config(self) -> dict:
            """Create the OpenMetadata workflow configuration"""
            sf_log("Creating OpenMetadata workflow configuration...")
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
                sf_log(f"Adding catalog file: {self.catalog_path}")
                config['source']['sourceConfig']['config']['dbtConfigSource']['dbtCatalogFilePath'] = self.catalog_path
            
            if self.run_results_path and Path(self.run_results_path).exists():
                sf_log(f"Adding run results file: {self.run_results_path}")
                config['source']['sourceConfig']['config']['dbtConfigSource']['dbtRunResultsFilePath'] = self.run_results_path
            
            sf_log("Configuration created successfully")
            return config
        
        def run(self) -> bool:
            """Execute the OpenMetadata ingestion workflow"""
            sf_log("Starting OpenMetadata ingestion workflow...")
            try:
                # Import OpenMetadata workflow
                try:
                    sf_log("Importing OpenMetadata workflow...")
                    from metadata.workflow.metadata import MetadataWorkflow
                    sf_log("OpenMetadata workflow imported successfully")
                except ImportError as import_error:
                    sf_log(f"❌ Error: openmetadata-ingestion package not found: {str(import_error)}")
                    sf_log("   Please install it with: pip install openmetadata-ingestion")
                    return False
                
                # Create configuration
                sf_log("Creating workflow configuration...")
                config = self._create_config()
                
                # Create workflow instance
                sf_log("Creating workflow instance...")
                workflow = MetadataWorkflow.create(config)
                sf_log("Workflow instance created successfully")
                
                # Execute the workflow
                sf_log("Executing workflow...")
                workflow.execute()
                sf_log("Workflow execution completed")
                
                sf_log("Checking workflow status...")
                workflow.raise_from_status()
                
                # Print the status
                sf_log("📊 Ingestion Summary:")
                try:
                    workflow.print_status()
                except Exception as status_error:
                    sf_log(f"Could not print workflow status: {str(status_error)}")
                
                sf_log("Stopping workflow...")
                workflow.stop()
                sf_log("Workflow stopped successfully")
                
                return True
                
            except Exception as e:
                sf_log(f"❌ Error during OpenMetadata ingestion: {str(e)}")
                sf_log(f"Exception type: {type(e).__name__}")
                import traceback
                sf_log(f"Traceback: {traceback.format_exc()}")
                return False

    try:
        sf_log("=== Starting dbt-col ingestion process ===")
        
        # Find dbt project
        sf_log("Step 1: Finding dbt project...")
        project_dir = find_dbt_project()
        if not project_dir:
            sf_log("❌ No dbt_project.yml found. Run from your dbt project directory or specify --project-dir.")
            return log_messages
        
        sf_log(f"📁 Found dbt project: {project_dir}")
        
        # Load dbt project configuration
        sf_log("Step 2: Loading dbt project configuration...")
        dbt_config = load_dbt_project_config(project_dir)
        vars_config = dbt_config.get('vars', {})
        sf_log(f"Found {len(vars_config)} variables in dbt config")
        
        # Extract OpenMetadata configuration
        sf_log("Step 3: Extracting OpenMetadata configuration...")
        jwt_token = vars_config.get('dbt_col_openmetadata_jwt_token')
        host_port = vars_config.get('dbt_col_openmetadata_host_port')
        service_name = vars_config.get('dbt_col_openmetadata_service_name', 'dbt')
        
        sf_log(f"JWT Token present: {'Yes' if jwt_token else 'No'}")
        sf_log(f"Host Port: {host_port if host_port else 'Not found'}")
        sf_log(f"Service Name: {service_name}")
        
        if not jwt_token or not host_port:
            sf_log("❌ OpenMetadata configuration not found in dbt_project.yml")
            sf_log("   Add the following to your vars:")
            sf_log("   dbt_col_openmetadata_jwt_token: 'your-jwt-token'")
            sf_log("   dbt_col_openmetadata_host_port: 'http://localhost:8585/api'")
            sf_log("   dbt_col_openmetadata_service_name: 'your-service-name'")
            return log_messages
        
        # Find target directory
        sf_log("Step 4: Checking target directory...")
        target_dir = project_dir / "target"
        sf_log(f"Target directory path: {target_dir}")
        if not target_dir.exists():
            sf_log("❌ Target directory not found. Please run 'dbt build' first.")
            return log_messages
        
        # Check for required artifacts
        sf_log("Step 5: Checking for required artifacts...")
        manifest_path = target_dir / "manifest.json"
        sf_log(f"Manifest path: {manifest_path}")
        if not manifest_path.exists():
            sf_log("❌ manifest.json not found. Please run 'dbt build' first.")
            return log_messages
        
        sf_log(f"🔗 Publishing to: {host_port}")
        sf_log(f"📊 Service name: {service_name}")
        
        # Create and run ingestion
        sf_log("Step 6: Creating ingestion instance...")
        ingestion = DbtColIngestion(
            host_port=host_port,
            jwt_token=jwt_token,
            service_name=service_name,
            manifest_path=str(manifest_path),
            catalog_path=str(target_dir / "catalog.json") if (target_dir / "catalog.json").exists() else None,
            run_results_path=str(target_dir / "run_results.json") if (target_dir / "run_results.json").exists() else None
        )
        
        sf_log("🚀 Starting OpenMetadata ingestion...")
        success = ingestion.run()
        
        if success:
            sf_log("✅ dbt-col: OpenMetadata ingestion completed successfully!")
        else:
            sf_log("❌ dbt-col: OpenMetadata ingestion failed.")
        
        sf_log("=== dbt-col ingestion process completed ===")
            
    except Exception as e:
        sf_log(f"❌ Error: {str(e)}")
        import traceback
        sf_log(f"Full traceback: {traceback.format_exc()}")
    
    print("OUTSIDE TEST FUNCTION")
    sys.stdout.flush()
    
    # Return the collected log messages
    return log_messages