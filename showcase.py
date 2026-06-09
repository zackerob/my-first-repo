"""
Python Capability Showcase
A single script demonstrating: OOP, file I/O, data processing,
concurrency, decorators, generators, context managers, and web requests.
"""

import json
import time
import threading
import statistics
import urllib.request
from pathlib import Path
from datetime import datetime
from functools import wraps
from dataclasses import dataclass, field
from typing import Generator


# ── 1. DECORATORS ─────────────────────────────────────────────────────────────

def timer(func):
    """Measures and prints how long a function takes to run."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  [{func.__name__}] took {elapsed:.4f}s")
        return result
    return wrapper


def retry(times=3, delay=0.5):
    """Retries a function up to `times` times on exception."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == times:
                        raise
                    print(f"  Attempt {attempt} failed ({e}), retrying...")
                    time.sleep(delay)
        return wrapper
    return decorator


# ── 2. DATACLASSES & OOP ──────────────────────────────────────────────────────

@dataclass
class Student:
    name: str
    grades: list[float] = field(default_factory=list)

    def add_grade(self, grade: float):
        self.grades.append(grade)

    @property
    def average(self) -> float:
        return statistics.mean(self.grades) if self.grades else 0.0

    @property
    def letter_grade(self) -> str:
        avg = self.average
        if avg >= 90: return "A"
        if avg >= 80: return "B"
        if avg >= 70: return "C"
        if avg >= 60: return "D"
        return "F"

    def __repr__(self):
        return f"Student({self.name!r}, avg={self.average:.1f}, grade={self.letter_grade})"


class Classroom:
    def __init__(self, name: str):
        self.name = name
        self._students: list[Student] = []

    def enroll(self, student: Student):
        self._students.append(student)

    def top_students(self, n=3) -> list[Student]:
        return sorted(self._students, key=lambda s: s.average, reverse=True)[:n]

    def class_average(self) -> float:
        return statistics.mean(s.average for s in self._students) if self._students else 0.0

    def __iter__(self):
        return iter(self._students)

    def __len__(self):
        return len(self._students)


# ── 3. GENERATORS ─────────────────────────────────────────────────────────────

def fibonacci() -> Generator[int, None, None]:
    """Infinite Fibonacci sequence — pulled lazily."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def primes_up_to(n: int) -> Generator[int, None, None]:
    """Sieve of Eratosthenes as a generator."""
    sieve = list(range(2, n + 1))
    for p in sieve:
        if p:
            yield p
            for multiple in range(p * p, n + 1, p):
                sieve[multiple - 2] = 0


# ── 4. CONTEXT MANAGERS ───────────────────────────────────────────────────────

class TempFile:
    """Creates a temporary JSON file, cleans it up on exit."""
    def __init__(self, path: str):
        self.path = Path(path)

    def __enter__(self):
        return self.path

    def __exit__(self, *_):
        if self.path.exists():
            self.path.unlink()
            print(f"  Cleaned up {self.path.name}")


# ── 5. CONCURRENCY ────────────────────────────────────────────────────────────

def worker(task_id: int, results: list, lock: threading.Lock):
    time.sleep(0.05)
    value = task_id ** 2
    with lock:
        results.append((task_id, value))


@timer
def run_concurrent_tasks(n=8):
    results, lock = [], threading.Lock()
    threads = [threading.Thread(target=worker, args=(i, results, lock)) for i in range(n)]
    for t in threads: t.start()
    for t in threads: t.join()
    results.sort()
    print(f"  Results: {results}")


# ── 6. FILE I/O & JSON ────────────────────────────────────────────────────────

@timer
def demo_file_io(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2))
    loaded = json.loads(path.read_text())
    print(f"  Saved and loaded {len(loaded)} keys from {path.name}")
    return loaded


# ── 7. WEB REQUEST ────────────────────────────────────────────────────────────

@retry(times=3, delay=1)
@timer
def fetch_joke() -> str:
    url = "https://official-joke-api.appspot.com/random_joke"
    with urllib.request.urlopen(url, timeout=5) as resp:
        data = json.loads(resp.read())
    return f"{data['setup']} — {data['punchline']}"


# ── 8. COMPREHENSIONS & FUNCTIONAL ────────────────────────────────────────────

def demo_data_processing(students: list[Student]):
    averages = {s.name: round(s.average, 1) for s in students}
    passing   = [s.name for s in students if s.average >= 70]
    by_grade  = {}
    for s in students:
        by_grade.setdefault(s.letter_grade, []).append(s.name)
    return averages, passing, by_grade


# ── MAIN ──────────────────────────────────────────────────────────────────────

def section(title: str):
    print(f"\n{'-' * 50}")
    print(f"  {title}")
    print(f"{'-' * 50}")


def main():
    print(f"\n{'=' * 50}")
    print("  Python Capability Showcase")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 50}")

    # OOP & Dataclasses
    section("1. OOP — Classroom & Students")
    room = Classroom("CS 101")
    raw_data = [
        ("Alice",   [92, 88, 95, 91]),
        ("Bob",     [74, 68, 79, 72]),
        ("Carol",   [85, 90, 88, 93]),
        ("Dave",    [55, 61, 58, 64]),
        ("Eve",     [98, 97, 99, 100]),
    ]
    for name, grades in raw_data:
        s = Student(name)
        for g in grades: s.add_grade(g)
        room.enroll(s)

    for student in room:
        print(f"  {student}")
    print(f"  Class average: {room.class_average():.1f}")
    print(f"  Top 3: {[s.name for s in room.top_students()]}")

    # Generators
    section("2. Generators")
    fib_gen = fibonacci()
    fibs = [next(fib_gen) for _ in range(12)]
    print(f"  First 12 Fibonacci: {fibs}")
    primes = list(primes_up_to(50))
    print(f"  Primes up to 50:    {primes}")

    # Data processing
    section("3. Comprehensions & Functional")
    averages, passing, by_grade = demo_data_processing(list(room))
    print(f"  Averages:  {averages}")
    print(f"  Passing:   {passing}")
    print(f"  By grade:  {by_grade}")

    # Concurrency
    section("4. Concurrency — 8 threads")
    run_concurrent_tasks(8)

    # File I/O
    section("5. File I/O & JSON")
    payload = {
        "timestamp": datetime.now().isoformat(),
        "students": [{"name": s.name, "avg": s.average} for s in room],
    }
    with TempFile("showcase_output.json") as tmp:
        demo_file_io(tmp, payload)

    # Web request
    section("6. Live Web Request — random joke")
    try:
        joke = fetch_joke()
        print(f"  {joke}")
    except Exception as e:
        print(f"  (Skipped — no internet or API down: {e})")

    # Decorators recap
    section("7. Decorators in action")
    print("  'timer' measured each timed function above.")
    print("  'retry' wraps fetch_joke with up to 3 attempts.")

    print(f"\n{'=' * 50}")
    print("  Done! Every section ran from a single script.")
    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    main()
