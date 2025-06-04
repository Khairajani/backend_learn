{% macro dbt_col_generate_and_run_ingestion(host_port, jwt_token, service_name, target_path, project_dir) %}
  {% set manifest_path = target_path ~ '/manifest.json' %}
  {% set catalog_path = target_path ~ '/catalog.json' %}
  {% set run_results_path = target_path ~ '/run_results.json' %}
  
  {# Generate the Python script content #}
  {% set python_script %}
import os
import sys
import tempfile
from pathlib import Path

try:
    from metadata.workflow.metadata import MetadataWorkflow
except ImportError:
    print("❌ Error: openmetadata-ingestion package not found.")
    print("   Please install it with: pip install openmetadata-ingestion")
    sys.exit(1)

def run_dbt_col_ingestion():
    """Run the DBT ingestion workflow using configuration from dbt vars"""
    try:
        # Configuration from dbt vars
        config = {
            'sink': {
                'config': {}, 
                'type': 'metadata-rest'
            },
            'source': {
                'serviceName': '{{ service_name }}',
                'sourceConfig': {
                    'config': {
                        'databaseFilterPattern': {
                            'includes': ['.*']
                        },
                        'dbtConfigSource': {
                            'dbtManifestFilePath': '{{ manifest_path }}',
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
                    'hostPort': '{{ host_port }}',
                    'securityConfig': {
                        'jwtToken': '{{ jwt_token }}'
                    }
                }
            }
        }

        # Add catalog and run_results if they exist
        catalog_path = Path('{{ catalog_path }}')
        if catalog_path.exists():
            config['source']['sourceConfig']['config']['dbtConfigSource']['dbtCatalogFilePath'] = '{{ catalog_path }}'
        
        run_results_path = Path('{{ run_results_path }}')
        if run_results_path.exists():
            config['source']['sourceConfig']['config']['dbtConfigSource']['dbtRunResultsFilePath'] = '{{ run_results_path }}'

        # Create workflow instance
        workflow = MetadataWorkflow.create(config)

        # Execute the workflow
        workflow.execute()
        workflow.raise_from_status()

        # Print the status
        print("✅ dbt-col: OpenMetadata ingestion completed successfully!")
        workflow.print_status()
        workflow.stop()

    except Exception as e:
        print(f"❌ dbt-col: Error during OpenMetadata ingestion: {str(e)}")
        raise

if __name__ == "__main__":
    run_dbt_col_ingestion()
  {% endset %}
  
  {# Write the script to a temporary file and execute it #}
  {% set script_path = target_path ~ '/dbt_col_ingestion.py' %}
  
  {# Log the script creation #}
  {% do log("📝 dbt-col: Generating ingestion script at " ~ script_path, info=True) %}
  
  {# Write script using dbt's local_var to store content temporarily #}
  {# This is a workaround since we can't directly write files from macros #}
  {% do log("🐍 dbt-col: Python ingestion script content:", info=True) %}
  {% do log("=" * 50, info=True) %}
  {% do log(python_script, info=True) %}
  {% do log("=" * 50, info=True) %}
  {% do log("💡 dbt-col: Copy the above script to " ~ script_path ~ " and run it manually, or use the CLI: dbt-col run", info=True) %}

{% endmacro %} 