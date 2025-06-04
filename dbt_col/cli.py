#!/usr/bin/env python3
"""
dbt-col CLI: Automated dbt to OpenMetadata publisher
"""

import argparse
import os
import sys
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Optional

from .core import DbtColIngestion


def find_dbt_project(start_path: Optional[Path] = None) -> Optional[Path]:
    """Find dbt_project.yml in current directory or parent directories"""
    current = start_path or Path.cwd()
    for path in [current] + list(current.parents):
        dbt_project = path / "dbt_project.yml"
        if dbt_project.exists():
            return path
    return None


def load_dbt_project_config(project_dir: Path) -> Dict:
    """Load dbt_project.yml configuration"""
    dbt_project_path = project_dir / "dbt_project.yml"
    with open(dbt_project_path, 'r') as f:
        return yaml.safe_load(f)


def auto_ingest_command(args):
    """Handle the auto-ingest command"""
    try:
        # Find dbt project
        project_dir = Path(args.project_dir) if args.project_dir else find_dbt_project()
        if not project_dir:
            print("❌ No dbt_project.yml found. Run from your dbt project directory or specify --project-dir.")
            sys.exit(1)
        
        print(f"📁 Found dbt project: {project_dir}")
        
        # Load dbt project configuration
        dbt_config = load_dbt_project_config(project_dir)
        vars_config = dbt_config.get('vars', {})
        
        # Extract OpenMetadata configuration
        jwt_token = vars_config.get('dbt_col_openmetadata_jwt_token')
        host_port = vars_config.get('dbt_col_openmetadata_host_port')
        service_name = vars_config.get('dbt_col_openmetadata_service_name', 'dbt')
        
        if not jwt_token or not host_port:
            print("❌ OpenMetadata configuration not found in dbt_project.yml")
            print("   Add the following to your vars:")
            print("   dbt_col_openmetadata_jwt_token: 'your-jwt-token'")
            print("   dbt_col_openmetadata_host_port: 'http://localhost:8585/api'")
            print("   dbt_col_openmetadata_service_name: 'your-service-name'")
            sys.exit(1)
        
        # Find target directory
        target_dir = project_dir / "target"
        if not target_dir.exists():
            print("❌ Target directory not found. Please run 'dbt build' first.")
            sys.exit(1)
        
        # Check for required artifacts
        manifest_path = target_dir / "manifest.json"
        if not manifest_path.exists():
            print("❌ manifest.json not found. Please run 'dbt build' first.")
            sys.exit(1)
        
        print(f"🔗 Publishing to: {host_port}")
        print(f"📊 Service name: {service_name}")
        
        # Create and run ingestion
        ingestion = DbtColIngestion(
            host_port=host_port,
            jwt_token=jwt_token,
            service_name=service_name,
            manifest_path=str(manifest_path),
            catalog_path=str(target_dir / "catalog.json") if (target_dir / "catalog.json").exists() else None,
            run_results_path=str(target_dir / "run_results.json") if (target_dir / "run_results.json").exists() else None
        )
        
        print("🚀 Starting OpenMetadata ingestion...")
        success = ingestion.run()
        
        if success:
            print("✅ dbt-col: OpenMetadata ingestion completed successfully!")
        else:
            print("❌ dbt-col: OpenMetadata ingestion failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def run_command(args):
    """Handle the run command (for manual execution)"""
    auto_ingest_command(args)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="dbt-col: Automated dbt to OpenMetadata publisher",
        prog="dbt-col"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Auto-ingest command (called by dbt hooks)
    auto_parser = subparsers.add_parser(
        'auto-ingest', 
        help='Automatically ingest dbt artifacts to OpenMetadata'
    )
    auto_parser.add_argument(
        '--project-dir', 
        help='Path to dbt project directory (auto-detected if not provided)'
    )
    auto_parser.set_defaults(func=auto_ingest_command)
    
    # Run command (for manual execution)
    run_parser = subparsers.add_parser(
        'run', 
        help='Run OpenMetadata ingestion manually'
    )
    run_parser.add_argument(
        '--project-dir', 
        help='Path to dbt project directory (auto-detected if not provided)'
    )
    run_parser.set_defaults(func=run_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    # Execute the appropriate command
    args.func(args)


if __name__ == "__main__":
    main() 