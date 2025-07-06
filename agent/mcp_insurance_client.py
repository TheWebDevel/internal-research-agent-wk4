import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPInsuranceClient:
    def __init__(self):
        current_dir = os.getcwd()
        self.server_params = StdioServerParameters(
            command="python",
            args=[os.path.join(current_dir, "mcp_server.py")],
            env=None,
        )
        print(f"[MCP Client] Initialized with server path: {os.path.join(current_dir, 'mcp_server.py')}")

    async def get_document_content(self, document_id: str) -> str:
        print(f"[MCP Client] Getting document content for ID: {document_id}")

        try:
            print(f"[MCP Client] Creating fresh connection...")
            stdio_ctx = stdio_client(self.server_params)
            read_stream, write_stream = await stdio_ctx.__aenter__()
            print(f"[MCP Client] Got read/write streams")

            session = await ClientSession(read_stream, write_stream).__aenter__()
            print(f"[MCP Client] Session created")

            await session.initialize()
            print(f"[MCP Client] Session initialized")

            print(f"[MCP Client] Calling get_document_content tool...")
            result = await session.call_tool("get_document_content", {"document_id": document_id})
            print(f"[MCP Client] Got result: {result}")

            if result.content and len(result.content) > 0:
                content = result.content[0]
                print(f"[MCP Client] Content type: {type(content)}")

                if hasattr(content, 'text') and hasattr(content, 'type') and content.type == "text":
                    print(f"[MCP Client] Retrieved content length: {len(content.text)}")
                    return content.text
                else:
                    return "Invalid response format from server"
            else:
                return "No response from server"

        except Exception as e:
            print(f"[MCP Client] Get document exception: {e}")
            print(f"[MCP Client] Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return f"Error retrieving document: {str(e)}"
        finally:
            try:
                if 'session' in locals():
                    await session.__aexit__(None, None, None)
                    print(f"[MCP Client] Session closed")
                if 'stdio_ctx' in locals():
                    await stdio_ctx.__aexit__(None, None, None)
                    print(f"[MCP Client] Stdio context closed")
            except Exception as cleanup_error:
                print(f"[MCP Client] Cleanup error: {cleanup_error}")


_insurance_client = None


def get_insurance_client() -> MCPInsuranceClient:
    global _insurance_client
    if _insurance_client is None:
        _insurance_client = MCPInsuranceClient()
    return _insurance_client


def run_async(coro):
    try:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(_run_in_new_loop, coro)
            return future.result(timeout=30)
    except Exception as e:
        print(f"Error in async operation: {e}")
        return f"Error: {str(e)}"


def _run_in_new_loop(coro):
    """Run coroutine in a new event loop."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except:
                pass
            loop.close()
    except Exception as e:
        print(f"Error in new loop: {e}")
        return f"Error: {str(e)}"