"""
MCP Server Configuration
========================

Configuration and startup script for the Pydantic MCP Server.
Provides easy setup and management of the Python execution server.

Based on https://ai.pydantic.dev/mcp/run-python/ guidelines.

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from .pydantic_mcp_server import PydanticMCPServer, get_server


class MCPServerConfig:
    """Configuration class for the MCP server."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (JSON)
        """
        self.config_file = config_file
        self.config = self._load_config()
        
        # Set up logging
        self._setup_logging()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "server": {
                "max_execution_time": 30,
                "enable_plotting": True,
                "temp_dir": None,
                "log_level": "INFO"
            },
            "plotting": {
                "default_style": "seaborn",
                "default_figure_size": [10, 6],
                "default_dpi": 100,
                "supported_formats": ["png", "svg", "pdf"]
            },
            "security": {
                "restricted_imports": [
                    "os", "sys", "subprocess", "importlib",
                    "__import__", "eval", "exec", "compile"
                ],
                "allowed_builtins": [
                    "abs", "all", "any", "bool", "dict", "enumerate",
                    "filter", "float", "int", "len", "list", "map",
                    "max", "min", "print", "range", "round", "sorted",
                    "str", "sum", "tuple", "type", "zip"
                ]
            },
            "libraries": {
                "required": ["matplotlib", "numpy", "seaborn"],
                "optional": ["pandas", "scipy", "scikit-learn", "plotly"]
            }
        }
        
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                # Merge with defaults
                self._deep_update(default_config, file_config)
            except Exception as e:
                print(f"Warning: Failed to load config file {self.config_file}: {e}")
        
        return default_config
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> Dict:
        """Deep update dictionary."""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict:
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
        return base_dict
    
    def _setup_logging(self):
        """Set up logging configuration."""
        log_level = getattr(logging, self.config["server"]["log_level"].upper())
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


class MCPServerManager:
    """Manager for the MCP server lifecycle."""
    
    def __init__(self, config: Optional[MCPServerConfig] = None):
        """
        Initialize server manager.
        
        Args:
            config: Server configuration
        """
        self.config = config or MCPServerConfig()
        self.server: Optional[PydanticMCPServer] = None
        self.is_running = False
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def start_server(self) -> PydanticMCPServer:
        """
        Start the MCP server.
        
        Returns:
            Started server instance
        """
        if self.is_running:
            return self.server
        
        self.logger.info("Starting Pydantic MCP Server...")
        
        try:
            # Create server with configuration
            server_config = self.config.config["server"]
            self.server = PydanticMCPServer(
                max_execution_time=server_config["max_execution_time"],
                temp_dir=server_config["temp_dir"],
                enable_plotting=server_config["enable_plotting"]
            )
            
            # Verify server health
            health = await self.server.health_check()
            
            if health["status"] != "healthy":
                raise RuntimeError(f"Server health check failed: {health}")
            
            self.is_running = True
            self.logger.info(f"MCP Server started successfully: {health['status']}")
            
            return self.server
            
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            raise
    
    async def stop_server(self):
        """Stop the MCP server."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping MCP Server...")
        
        try:
            # Cleanup if needed
            self.server = None
            self.is_running = False
            
            self.logger.info("MCP Server stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping MCP server: {e}")
    
    async def restart_server(self) -> PydanticMCPServer:
        """
        Restart the MCP server.
        
        Returns:
            Restarted server instance
        """
        await self.stop_server()
        return await self.start_server()
    
    async def get_server_status(self) -> Dict[str, Any]:
        """
        Get current server status.
        
        Returns:
            Status dictionary
        """
        status = {
            "is_running": self.is_running,
            "config": self.config.config,
            "server": None
        }
        
        if self.server and self.is_running:
            try:
                health = await self.server.health_check()
                status["server"] = health
            except Exception as e:
                status["server"] = {"error": str(e)}
        
        return status


class MCPServerCLI:
    """Command line interface for the MCP server."""
    
    def __init__(self):
        self.manager = MCPServerManager()
    
    async def run_health_check(self):
        """Run a health check on the server."""
        print("Running MCP Server health check...")
        
        try:
            server = await self.manager.start_server()
            health = await server.health_check()
            
            print(f"Server Status: {health['status']}")
            print(f"Python Version: {health['python_version']}")
            print(f"Plotting Enabled: {health['plotting_enabled']}")
            
            if "test_execution" in health:
                print(f"Test Execution: {health['test_execution']['success']}")
            
            if "test_plotting" in health:
                print(f"Test Plotting: {health['test_plotting']['success']}")
                if health['test_plotting']['success']:
                    print(f"Plots Generated: {health['test_plotting']['plots_generated']}")
            
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
        
        return True
    
    async def run_example_chart(self):
        """Run an example chart generation."""
        print("Running example chart generation...")
        
        try:
            server = await self.manager.start_server()
            
            # Sample data
            data = {
                "labels": ["January", "February", "March", "April", "May", "June"],
                "values": [65, 59, 80, 81, 56, 55]
            }
            
            # Generate bar chart
            result = await server.create_chart("bar", data, "Monthly Sales")
            
            print(f"Chart Generation Success: {result.success}")
            print(f"Execution Time: {result.execution_time:.2f}s")
            print(f"Plots Generated: {len(result.plots)}")
            
            if result.plots:
                # Save example chart
                chart_data = result.plots[0]
                output_file = "example_chart.png"
                
                import base64
                with open(output_file, "wb") as f:
                    f.write(base64.b64decode(chart_data))
                
                print(f"Example chart saved to: {output_file}")
                print(f"Base64 length: {len(chart_data)} characters")
            
            if result.stdout:
                print(f"Output: {result.stdout}")
            
            if not result.success:
                print(f"Error: {result.error_message}")
                if result.stderr:
                    print(f"Stderr: {result.stderr}")
        
        except Exception as e:
            print(f"Example chart generation failed: {e}")
            return False
        
        return True
    
    async def interactive_mode(self):
        """Run in interactive mode."""
        print("Starting MCP Server interactive mode...")
        print("Type 'help' for commands, 'quit' to exit")
        
        try:
            server = await self.manager.start_server()
            
            while True:
                try:
                    code = input("\n>>> ")
                    
                    if code.lower() in ['quit', 'exit', 'q']:
                        break
                    elif code.lower() == 'help':
                        print("Commands:")
                        print("  help - Show this help")
                        print("  quit - Exit interactive mode")
                        print("  health - Run health check")
                        print("  example - Generate example chart")
                        print("  Or enter Python code to execute")
                        continue
                    elif code.lower() == 'health':
                        health = await server.health_check()
                        print(f"Status: {health['status']}")
                        continue
                    elif code.lower() == 'example':
                        await self.run_example_chart()
                        continue
                    
                    # Execute the code
                    from .pydantic_mcp_server import PythonExecutionRequest
                    request = PythonExecutionRequest(code=code)
                    result = await server.execute_python_code(request)
                    
                    if result.success:
                        if result.stdout:
                            print(result.stdout)
                        if result.plots:
                            print(f"Generated {len(result.plots)} plot(s)")
                    else:
                        print(f"Error ({result.error_type}): {result.error_message}")
                        if result.stderr:
                            print(result.stderr)
                
                except KeyboardInterrupt:
                    print("\nUse 'quit' to exit")
                    continue
                except Exception as e:
                    print(f"Error: {e}")
        
        finally:
            await self.manager.stop_server()
            print("MCP Server stopped")


def create_sample_config(filename: str = "mcp_server_config.json"):
    """Create a sample configuration file."""
    sample_config = {
        "server": {
            "max_execution_time": 30,
            "enable_plotting": True,
            "temp_dir": None,
            "log_level": "INFO"
        },
        "plotting": {
            "default_style": "seaborn",
            "default_figure_size": [10, 6],
            "default_dpi": 100
        },
        "security": {
            "restricted_mode": True
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"Sample configuration created: {filename}")


if __name__ == "__main__":
    async def main():
        cli = MCPServerCLI()
        
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "health":
                success = await cli.run_health_check()
                sys.exit(0 if success else 1)
            
            elif command == "example":
                success = await cli.run_example_chart()
                sys.exit(0 if success else 1)
            
            elif command == "config":
                create_sample_config()
                sys.exit(0)
            
            elif command == "interactive":
                await cli.interactive_mode()
                sys.exit(0)
            
            else:
                print("Usage: python mcp_server_config.py [health|example|config|interactive]")
                sys.exit(1)
        
        else:
            # Default: run health check and example
            print("Running MCP Server demo...")
            
            health_ok = await cli.run_health_check()
            if health_ok:
                await cli.run_example_chart()
            
            print("\nDemo complete!")
    
    # Run the CLI
    asyncio.run(main())