import numpy as np
from typing import Dict, List, Any
import torch
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor
import mmap
import asyncio
from dataclasses import dataclass
import weakref

class SharedMemoryPool:
    """Zero-copy shared memory pool for all agents"""
    def __init__(self, size_mb: int = 1024):
        self.memory_size = size_mb * 1024 * 1024
        self.memory = mmap.mmap(-1, self.memory_size)
        self.allocated = {}
        self._lock = threading.Lock()
        
    def allocate(self, size: int) -> memoryview:
        with self._lock:
            view = memoryview(self.memory)[len(self.allocated):len(self.allocated)+size]
            self.allocated[id(view)] = size
            return view
            
    def free(self, view: memoryview):
        with self._lock:
            if id(view) in self.allocated:
                del self.allocated[id(view)]
                view.release()

class ModelPool:
    """Shared AI models pool"""
    _models: Dict[str, Any] = {}
    _locks: Dict[str, threading.Lock] = {}
    
    @classmethod
    def get_model(cls, model_name: str) -> Any:
        if model_name not in cls._models:
            with cls._locks.get(model_name, threading.Lock()):
                if model_name not in cls._models:
                    cls._models[model_name] = cls._load_model(model_name)
        return cls._models[model_name]
    
    @staticmethod
    def _load_model(model_name: str) -> Any:
        # Load models efficiently using torch.jit for GPU optimization
        if model_name == "price_predictor":
            return torch.jit.load("models/price_predictor.pt")
        elif model_name == "pattern_recognizer":
            return torch.jit.load("models/pattern_recognizer.pt")
        # Add more models as needed

class DataStream:
    """Efficient market data streaming"""
    def __init__(self, max_items: int = 1000):
        self.data = deque(maxlen=max_items)
        self.subscribers = weakref.WeakSet()
        self._lock = asyncio.Lock()
        
    async def push(self, data: Dict):
        async with self._lock:
            self.data.append(data)
            await self._notify_subscribers(data)
            
    async def _notify_subscribers(self, data: Dict):
        for subscriber in self.subscribers:
            await subscriber(data)
            
    def subscribe(self, callback):
        self.subscribers.add(callback)
        
    def unsubscribe(self, callback):
        self.subscribers.remove(callback)

@dataclass
class AgentState:
    """Efficient agent state storage"""
    id: str
    type: str
    status: str
    memory_view: memoryview
    model_refs: List[str]
    active_trades: Dict
    
    def __del__(self):
        if hasattr(self, 'memory_view'):
            self.memory_view.release()

class SharedResources:
    """Central resource manager"""
    def __init__(self):
        self.memory_pool = SharedMemoryPool()
        self.model_pool = ModelPool()
        self.market_stream = DataStream()
        self.agent_states: Dict[str, AgentState] = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=32)
        self._lock = threading.Lock()
        
    async def register_agent(self, agent_id: str, agent_type: str) -> AgentState:
        """Register new agent and allocate resources"""
        with self._lock:
            memory = self.memory_pool.allocate(1024 * 1024)  # 1MB per agent
            state = AgentState(
                id=agent_id,
                type=agent_type,
                status="initialized",
                memory_view=memory,
                model_refs=[],
                active_trades={}
            )
            self.agent_states[agent_id] = state
            return state
            
    async def unregister_agent(self, agent_id: str):
        """Clean up agent resources"""
        with self._lock:
            if agent_id in self.agent_states:
                state = self.agent_states[agent_id]
                self.memory_pool.free(state.memory_view)
                del self.agent_states[agent_id]
                
    def get_model(self, model_name: str) -> Any:
        """Get shared model instance"""
        return self.model_pool.get_model(model_name)
        
    async def execute_task(self, func, *args):
        """Execute CPU-bound task in thread pool"""
        return await asyncio.get_event_loop().run_in_executor(
            self.thread_pool, func, *args
        )

# Global shared resources instance
SHARED_RESOURCES = SharedResources()
