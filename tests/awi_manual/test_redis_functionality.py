#!/usr/bin/env python3
"""
Redis Functionality Test Automation

Comprehensive testing suite for Redis functionality including:
- Connection and authentication
- Basic operations (set, get, delete, exists)
- Data types (strings, hashes, lists, sets, sorted sets)
- Expiration and TTL
- Transactions and pipelining
- Pub/Sub messaging
- Rate limiting patterns
- Session management patterns
- Performance benchmarks

Usage:
    python test_redis_functionality.py
"""

import asyncio
import time
import sys
import os
from typing import Dict, Any, List
from dataclasses import dataclass
import json

try:
	import redis.asyncio as redis
	from redis.exceptions import ConnectionError, TimeoutError, RedisError
except ImportError:
	print("❌ Redis package not found. Install with: pip install redis")
	sys.exit(1)

try:
	from dotenv import load_dotenv
	load_dotenv()
except ImportError:
	pass  # dotenv optional


@dataclass
class TestResult:
	"""Result of a single test."""
	name: str
	passed: bool
	duration: float
	message: str = ""
	error: str = ""


class RedisTestSuite:
	"""Comprehensive Redis test suite."""

	def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: str = None):
		"""Initialize test suite with Redis connection parameters."""
		self.host = host
		self.port = port
		self.db = db
		self.password = password
		self.client = None
		self.results: List[TestResult] = []

	async def connect(self) -> bool:
		"""Establish Redis connection."""
		try:
			self.client = redis.Redis(
				host=self.host,
				port=self.port,
				db=self.db,
				password=self.password,
				decode_responses=True,
				socket_timeout=5,
				socket_connect_timeout=5
			)
			# Test connection
			await self.client.ping()
			return True
		except Exception as e:
			print(f"❌ Failed to connect to Redis: {e}")
			return False

	async def disconnect(self):
		"""Close Redis connection."""
		if self.client:
			await self.client.close()

	async def run_test(self, name: str, test_func):
		"""Run a single test and record results."""
		print(f"\n   Testing: {name}...", end=" ")
		start_time = time.time()

		try:
			await test_func()
			duration = time.time() - start_time
			self.results.append(TestResult(name, True, duration, "Passed"))
			print(f"✅ ({duration:.3f}s)")
			return True

		except Exception as e:
			duration = time.time() - start_time
			error_msg = str(e)[:100]
			self.results.append(TestResult(name, False, duration, error=error_msg))
			print(f"❌ ({duration:.3f}s)")
			print(f"      Error: {error_msg}")
			return False

	# ==================== Connection Tests ====================

	async def test_connection(self):
		"""Test basic Redis connection."""
		result = await self.client.ping()
		assert result is True, "Ping failed"

	async def test_info(self):
		"""Test Redis INFO command."""
		info = await self.client.info()
		assert isinstance(info, dict), "INFO command failed"
		assert "redis_version" in info, "Missing Redis version"

	# ==================== Basic Operation Tests ====================

	async def test_string_operations(self):
		"""Test string set/get operations."""
		key = "test:string"
		value = "Hello, Redis!"

		# Set
		await self.client.set(key, value)

		# Get
		result = await self.client.get(key)
		assert result == value, f"Expected '{value}', got '{result}'"

		# Delete
		await self.client.delete(key)

		# Verify deletion
		result = await self.client.get(key)
		assert result is None, "Key should be deleted"

	async def test_numeric_operations(self):
		"""Test numeric increment/decrement operations."""
		key = "test:counter"

		# Set initial value
		await self.client.set(key, 0)

		# Increment
		result = await self.client.incr(key)
		assert result == 1, f"Expected 1, got {result}"

		# Increment by amount
		result = await self.client.incrby(key, 10)
		assert result == 11, f"Expected 11, got {result}"

		# Decrement
		result = await self.client.decr(key)
		assert result == 10, f"Expected 10, got {result}"

		# Cleanup
		await self.client.delete(key)

	async def test_exists_and_keys(self):
		"""Test key existence and pattern matching."""
		keys = ["test:key1", "test:key2", "test:key3"]

		# Set keys
		for key in keys:
			await self.client.set(key, "value")

		# Test exists
		for key in keys:
			exists = await self.client.exists(key)
			assert exists == 1, f"Key {key} should exist"

		# Test keys pattern
		found_keys = await self.client.keys("test:key*")
		assert len(found_keys) >= 3, f"Expected at least 3 keys, found {len(found_keys)}"

		# Cleanup
		await self.client.delete(*keys)

	# ==================== Data Type Tests ====================

	async def test_hash_operations(self):
		"""Test hash (dictionary) operations."""
		key = "test:hash"

		# Set hash fields
		await self.client.hset(key, "name", "John")
		await self.client.hset(key, "age", "30")
		await self.client.hset(key, "city", "NYC")

		# Get single field
		name = await self.client.hget(key, "name")
		assert name == "John", f"Expected 'John', got '{name}'"

		# Get all fields
		data = await self.client.hgetall(key)
		assert len(data) == 3, f"Expected 3 fields, got {len(data)}"
		assert data["age"] == "30", "Age mismatch"

		# Delete field
		await self.client.hdel(key, "city")
		exists = await self.client.hexists(key, "city")
		assert exists == 0, "City field should be deleted"

		# Cleanup
		await self.client.delete(key)

	async def test_list_operations(self):
		"""Test list (queue) operations."""
		key = "test:list"

		# Push items
		await self.client.rpush(key, "item1", "item2", "item3")

		# Get list length
		length = await self.client.llen(key)
		assert length == 3, f"Expected length 3, got {length}"

		# Get range
		items = await self.client.lrange(key, 0, -1)
		assert items == ["item1", "item2", "item3"], "List mismatch"

		# Pop items
		item = await self.client.lpop(key)
		assert item == "item1", f"Expected 'item1', got '{item}'"

		# Cleanup
		await self.client.delete(key)

	async def test_set_operations(self):
		"""Test set (unique collection) operations."""
		key = "test:set"

		# Add members
		await self.client.sadd(key, "member1", "member2", "member3")

		# Check membership
		is_member = await self.client.sismember(key, "member1")
		assert is_member == 1, "member1 should be in set"

		# Get all members
		members = await self.client.smembers(key)
		assert len(members) == 3, f"Expected 3 members, got {len(members)}"

		# Remove member
		await self.client.srem(key, "member2")
		size = await self.client.scard(key)
		assert size == 2, f"Expected 2 members, got {size}"

		# Cleanup
		await self.client.delete(key)

	async def test_sorted_set_operations(self):
		"""Test sorted set operations."""
		key = "test:zset"

		# Add scored members
		await self.client.zadd(key, {"user1": 100, "user2": 200, "user3": 150})

		# Get rank
		rank = await self.client.zrank(key, "user1")
		assert rank == 0, f"Expected rank 0, got {rank}"

		# Get score
		score = await self.client.zscore(key, "user2")
		assert score == 200.0, f"Expected score 200, got {score}"

		# Get range by score
		members = await self.client.zrangebyscore(key, 100, 200)
		assert len(members) == 3, f"Expected 3 members, got {len(members)}"

		# Cleanup
		await self.client.delete(key)

	# ==================== Expiration Tests ====================

	async def test_expiration(self):
		"""Test key expiration and TTL."""
		key = "test:expire"

		# Set with expiration
		await self.client.setex(key, 2, "temporary")

		# Check TTL
		ttl = await self.client.ttl(key)
		assert ttl > 0 and ttl <= 2, f"Expected TTL <= 2, got {ttl}"

		# Wait for expiration
		await asyncio.sleep(2.5)

		# Verify expiration
		exists = await self.client.exists(key)
		assert exists == 0, "Key should have expired"

	async def test_persist(self):
		"""Test removing expiration from keys."""
		key = "test:persist"

		# Set with expiration
		await self.client.setex(key, 10, "value")

		# Check TTL
		ttl = await self.client.ttl(key)
		assert ttl > 0, "Key should have TTL"

		# Remove expiration
		await self.client.persist(key)

		# Check TTL again
		ttl = await self.client.ttl(key)
		assert ttl == -1, "Key should not have TTL after persist"

		# Cleanup
		await self.client.delete(key)

	# ==================== Transaction Tests ====================

	async def test_pipeline(self):
		"""Test pipelined commands for performance."""
		keys = [f"test:pipe:{i}" for i in range(10)]

		# Use pipeline
		pipe = self.client.pipeline()
		for i, key in enumerate(keys):
			pipe.set(key, f"value{i}")
		results = await pipe.execute()

		assert len(results) == 10, f"Expected 10 results, got {len(results)}"

		# Verify values
		for i, key in enumerate(keys):
			value = await self.client.get(key)
			assert value == f"value{i}", f"Value mismatch for {key}"

		# Cleanup
		await self.client.delete(*keys)

	async def test_multi_exec(self):
		"""Test atomic transactions with MULTI/EXEC."""
		key = "test:transaction"

		# Start transaction
		pipe = self.client.pipeline()
		pipe.set(key, 0)
		pipe.incr(key)
		pipe.incr(key)
		pipe.incr(key)
		results = await pipe.execute()

		# Check final value
		value = await self.client.get(key)
		assert value == "3", f"Expected '3', got '{value}'"

		# Cleanup
		await self.client.delete(key)

	# ==================== Session Management Pattern Tests ====================

	async def test_session_pattern(self):
		"""Test session management pattern (AWI use case)."""
		session_id = "sess_test123"
		session_key = f"session:{session_id}"

		# Create session
		session_data = {
			"user_id": "user123",
			"created_at": str(time.time()),
			"actions": "0"
		}

		await self.client.hset(session_key, mapping=session_data)
		await self.client.expire(session_key, 3600)  # 1 hour

		# Update session
		await self.client.hincrby(session_key, "actions", 1)

		# Retrieve session
		retrieved = await self.client.hgetall(session_key)
		assert retrieved["user_id"] == "user123", "User ID mismatch"
		assert retrieved["actions"] == "1", "Actions count mismatch"

		# Cleanup
		await self.client.delete(session_key)

	async def test_rate_limiting_pattern(self):
		"""Test rate limiting pattern (AWI use case)."""
		user_id = "user123"
		rate_key = f"rate:{user_id}"

		# Simulate rate limiting (10 requests per minute)
		for i in range(5):
			count = await self.client.incr(rate_key)
			if count == 1:
				await self.client.expire(rate_key, 60)

		# Check count
		count = await self.client.get(rate_key)
		assert int(count) == 5, f"Expected 5 requests, got {count}"

		# Cleanup
		await self.client.delete(rate_key)

	async def test_caching_pattern(self):
		"""Test caching pattern with JSON data."""
		cache_key = "cache:post:123"

		# Cache data
		post_data = {
			"id": 123,
			"title": "Test Post",
			"content": "Content here",
			"views": 42
		}

		await self.client.setex(cache_key, 300, json.dumps(post_data))

		# Retrieve cached data
		cached = await self.client.get(cache_key)
		retrieved_data = json.loads(cached)

		assert retrieved_data["id"] == 123, "ID mismatch"
		assert retrieved_data["views"] == 42, "Views mismatch"

		# Cleanup
		await self.client.delete(cache_key)

	# ==================== Performance Tests ====================

	async def test_performance_write(self):
		"""Test write performance."""
		count = 1000
		keys = [f"test:perf:write:{i}" for i in range(count)]

		start = time.time()

		# Write using pipeline
		pipe = self.client.pipeline()
		for key in keys:
			pipe.set(key, "value")
		await pipe.execute()

		duration = time.time() - start
		ops_per_sec = count / duration

		print(f"\n      Write: {count} ops in {duration:.3f}s = {ops_per_sec:.0f} ops/sec")

		assert ops_per_sec > 100, f"Write performance too slow: {ops_per_sec:.0f} ops/sec"

		# Cleanup
		await self.client.delete(*keys)

	async def test_performance_read(self):
		"""Test read performance."""
		count = 1000
		keys = [f"test:perf:read:{i}" for i in range(count)]

		# Setup data
		pipe = self.client.pipeline()
		for key in keys:
			pipe.set(key, "value")
		await pipe.execute()

		start = time.time()

		# Read using pipeline
		pipe = self.client.pipeline()
		for key in keys:
			pipe.get(key)
		await pipe.execute()

		duration = time.time() - start
		ops_per_sec = count / duration

		print(f"\n      Read: {count} ops in {duration:.3f}s = {ops_per_sec:.0f} ops/sec")

		assert ops_per_sec > 100, f"Read performance too slow: {ops_per_sec:.0f} ops/sec"

		# Cleanup
		await self.client.delete(*keys)

	# ==================== Run All Tests ====================

	async def run_all_tests(self) -> Dict[str, Any]:
		"""Run all tests and return summary."""
		print("\n" + "=" * 80)
		print("🧪 REDIS FUNCTIONALITY TEST SUITE")
		print("=" * 80)

		print(f"\n📋 Configuration:")
		print(f"   Host: {self.host}:{self.port}")
		print(f"   Database: {self.db}")

		# Connect
		print("\n🔌 Connecting to Redis...", end=" ")
		if not await self.connect():
			return {
				"success": False,
				"error": "Failed to connect to Redis",
				"total": 0,
				"passed": 0,
				"failed": 0
			}
		print("✅")

		# Get Redis info
		info = await self.client.info()
		print(f"   Redis Version: {info.get('redis_version', 'unknown')}")
		print(f"   Used Memory: {info.get('used_memory_human', 'unknown')}")

		# Run tests by category
		categories = [
			("Connection Tests", [
				("Ping", self.test_connection),
				("Info Command", self.test_info),
			]),
			("Basic Operations", [
				("String Operations", self.test_string_operations),
				("Numeric Operations", self.test_numeric_operations),
				("Exists and Keys", self.test_exists_and_keys),
			]),
			("Data Types", [
				("Hash Operations", self.test_hash_operations),
				("List Operations", self.test_list_operations),
				("Set Operations", self.test_set_operations),
				("Sorted Set Operations", self.test_sorted_set_operations),
			]),
			("Expiration & TTL", [
				("Key Expiration", self.test_expiration),
				("Persist Key", self.test_persist),
			]),
			("Transactions", [
				("Pipeline", self.test_pipeline),
				("Multi/Exec", self.test_multi_exec),
			]),
			("AWI Patterns", [
				("Session Management", self.test_session_pattern),
				("Rate Limiting", self.test_rate_limiting_pattern),
				("Caching", self.test_caching_pattern),
			]),
			("Performance", [
				("Write Performance", self.test_performance_write),
				("Read Performance", self.test_performance_read),
			]),
		]

		# Run all tests
		for category_name, tests in categories:
			print(f"\n📦 {category_name}")
			for test_name, test_func in tests:
				await self.run_test(test_name, test_func)

		# Disconnect
		await self.disconnect()

		# Generate summary
		total = len(self.results)
		passed = sum(1 for r in self.results if r.passed)
		failed = total - passed
		success_rate = (passed / total * 100) if total > 0 else 0

		print("\n" + "=" * 80)
		print("📊 TEST RESULTS SUMMARY")
		print("=" * 80)

		print(f"\n   Total Tests: {total}")
		print(f"   ✅ Passed: {passed}")
		print(f"   ❌ Failed: {failed}")
		print(f"   Success Rate: {success_rate:.1f}%")

		if failed > 0:
			print(f"\n❌ Failed Tests:")
			for result in self.results:
				if not result.passed:
					print(f"   • {result.name}")
					print(f"     Error: {result.error}")

		print("\n" + "=" * 80)

		if failed == 0:
			print("🎉 ALL TESTS PASSED!")
		else:
			print(f"⚠️  {failed} TEST(S) FAILED")

		print("=" * 80 + "\n")

		return {
			"success": failed == 0,
			"total": total,
			"passed": passed,
			"failed": failed,
			"success_rate": success_rate,
			"results": [
				{
					"name": r.name,
					"passed": r.passed,
					"duration": r.duration,
					"error": r.error
				}
				for r in self.results
			]
		}


async def main():
	"""Main test execution."""
	import argparse

	parser = argparse.ArgumentParser(description="Redis Functionality Test Suite")
	parser.add_argument("--host", default="localhost", help="Redis host (default: localhost)")
	parser.add_argument("--port", type=int, default=6379, help="Redis port (default: 6379)")
	parser.add_argument("--db", type=int, default=0, help="Redis database number (default: 0)")
	parser.add_argument("--password", default=None, help="Redis password (optional, defaults to REDIS_PASSWORD env var)")
	args = parser.parse_args()

	# Get password from args or environment
	password = args.password or os.getenv("REDIS_PASSWORD")

	# Run tests
	suite = RedisTestSuite(
		host=args.host,
		port=args.port,
		db=args.db,
		password=password
	)

	try:
		summary = await suite.run_all_tests()
		sys.exit(0 if summary["success"] else 1)
	except KeyboardInterrupt:
		print("\n\n⚠️  Tests interrupted by user")
		sys.exit(1)
	except Exception as e:
		print(f"\n\n❌ Unexpected error: {e}")
		import traceback
		traceback.print_exc()
		sys.exit(1)


if __name__ == "__main__":
	asyncio.run(main())
