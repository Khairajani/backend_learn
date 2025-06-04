{% macro on_run_end() %}
  {% if execute %}
    {# Check if OpenMetadata config exists #}
    {% set jwt_token = var('dbt_col_openmetadata_jwt_token', none) %}
    {% set host_port = var('dbt_col_openmetadata_host_port', none) %}
    {% set service_name = var('dbt_col_openmetadata_service_name', 'dbt') %}
    
    {% if jwt_token and host_port %}
      {% do log("🚀 dbt-col: OpenMetadata configuration found!", info=True) %}
      {% do log("📊 Service: " ~ service_name ~ " | Host: " ~ host_port, info=True) %}
      {% do log("💡 To publish metadata to OpenMetadata, run:", info=True) %}
      {% do log("   dbt-col auto-ingest", info=True) %}
      {% do log("", info=True) %}
      
    {% else %}
      {% do log("ℹ️  dbt-col: OpenMetadata configuration not found.", info=True) %}
      {% do log("   Add the following to your dbt_project.yml vars:", info=True) %}
      {% do log("   dbt_col_openmetadata_jwt_token: 'your-jwt-token'", info=True) %}
      {% do log("   dbt_col_openmetadata_host_port: 'http://localhost:8585/api'", info=True) %}
      {% do log("   dbt_col_openmetadata_service_name: 'your-service-name'", info=True) %}
    {% endif %}
    
  {% endif %}
{% endmacro %} 