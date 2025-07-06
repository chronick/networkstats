# Network Monitoring and Logging Specification: Monitoring Engine Architecture



## Async Task Management

class MonitoringEngine:
    def __init__(self, config: dict):
        self.config = config
        self.ping_strategy = PingStrategy()
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 10))
        self.tasks: dict[str, asyncio.Task] = {}
    
    async def monitor_target(self, target: str):
        """Monitor a single target continuously."""
        interval = self.config['interval_sec']
        
        while True:
            try:
                latency = await self.ping_strategy.ping(target)
                success = latency is not None
                
                # Record result
                await self.record_result(target, latency or 0.0, success)
                
                # Emit event for UI updates
                await self.emit_event('ping_result', {
                    'target': target,
                    'latency': latency,
                    'success': success,
                    'timestamp': time.time()
                })
                
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Error monitoring {target}: {e}")
            
            await asyncio.sleep(interval)

```python
class MonitoringEngine:
    def __init__(self, config: dict):
        self.config = config
        self.ping_strategy = PingStrategy()
        self.executor = ThreadPoolExecutor(max_workers=config.get('max_workers', 10))
        self.tasks: dict[str, asyncio.Task] = {}
    
    async def monitor_target(self, target: str):
        """Monitor a single target continuously."""
        interval = self.config['interval_sec']
        
        while True:
            try:
                latency = await self.ping_strategy.ping(target)
                success = latency is not None
                
                # Record result
                await self.record_result(target, latency or 0.0, success)
                
                # Emit event for UI updates
                await self.emit_event('ping_result', {
                    'target': target,
                    'latency': latency,
                    'success': success,
                    'timestamp': time.time()
                })
                
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Error monitoring {target}: {e}")
            
            await asyncio.sleep(interval)

```

## Dynamic Target Management

async def add_target(self, target: str):
    """Add a new monitoring target."""
    if target not in self.tasks:
        task = asyncio.create_task(self.monitor_target(target))
        self.tasks[target] = task
        logger.info(f"Added monitoring target: {target}")

async def remove_target(self, target: str):
    """Remove a monitoring target."""
    if target in self.tasks:
        self.tasks[target].cancel()
        await self.tasks[target]
        del self.tasks[target]
        logger.info(f"Removed monitoring target: {target}")

```python
async def add_target(self, target: str):
    """Add a new monitoring target."""
    if target not in self.tasks:
        task = asyncio.create_task(self.monitor_target(target))
        self.tasks[target] = task
        logger.info(f"Added monitoring target: {target}")

async def remove_target(self, target: str):
    """Remove a monitoring target."""
    if target in self.tasks:
        self.tasks[target].cancel()
        await self.tasks[target]
        del self.tasks[target]
        logger.info(f"Removed monitoring target: {target}")

```
