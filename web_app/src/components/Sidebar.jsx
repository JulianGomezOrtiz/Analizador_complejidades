import React from 'react'
import { FileCode, Terminal } from 'lucide-react'
import clsx from 'clsx'

export function Sidebar({ onSelectAlgorithm, selectedAlgorithm }) {
  const algorithms = [
    {
      name: 'Insertion Sort',
      id: 'insertionSort',
      code: `PROCEDURE InsertionSort(A, n)
BEGIN
  FOR i <- 2 TO n DO
  BEGIN
    key <- A[i];
    j <- i - 1;
    WHILE j > 0 and A[j] > key DO
    BEGIN
      A[j+1] <- A[j];
      j <- j - 1;
    END
    A[j+1] <- key;
  END
END`
    },
    {
      name: 'Selection Sort',
      id: 'selectionSort',
      code: `PROCEDURE SelectionSort(A, n)
BEGIN
  FOR i <- 1 TO n - 1 DO
  BEGIN
    min_idx <- i;
    FOR j <- i + 1 TO n DO
    BEGIN
      IF A[j] < A[min_idx] THEN
        min_idx <- j;
      ENDIF
    END
    temp <- A[min_idx];
    A[min_idx] <- A[i];
    A[i] <- temp;
  END
END`
    },
    {
      name: 'Bubble Sort',
      id: 'bubbleSort',
      code: `PROCEDURE BubbleSort(A, n)
BEGIN
  FOR i <- 1 TO n - 1 DO
  BEGIN
    FOR j <- n TO i + 1 STEP -1 DO
    BEGIN
      IF A[j] < A[j-1] THEN
      BEGIN
        temp <- A[j];
        A[j] <- A[j-1];
        A[j-1] <- temp;
      END
      ENDIF
    END
  END
END`
    },
    {
      name: 'Merge Sort',
      id: 'mergeSort',
      code: `PROCEDURE MergeSort(A, p, r)
BEGIN
  IF p < r THEN
  BEGIN
    q <- floor((p + r) / 2);
    CALL MergeSort(A, p, q);
    CALL MergeSort(A, q + 1, r);
    CALL Merge(A, p, q, r);
  END
  ENDIF
END`
    },
    {
      name: 'Quick Sort',
      id: 'quickSort',
      code: `PROCEDURE QuickSort(A, p, r)
BEGIN
  IF p < r THEN
  BEGIN
    q <- Partition(A, p, r);
    CALL QuickSort(A, p, q - 1);
    CALL QuickSort(A, q + 1, r);
  END
  ENDIF
END`
    },
    {
      name: 'Heap Sort',
      id: 'heapSort',
      code: `PROCEDURE MaxHeapify(A, i, n)
BEGIN
  l <- 2 * i;
  r <- 2 * i + 1;
  largest <- i;
  IF l <= n and A[l] > A[largest] THEN
    largest <- l;
  ENDIF
  IF r <= n and A[r] > A[largest] THEN
    largest <- r;
  ENDIF
  IF largest <> i THEN
  BEGIN
    temp <- A[i];
    A[i] <- A[largest];
    A[largest] <- temp;
    CALL MaxHeapify(A, largest, n);
  END
  ENDIF
END

PROCEDURE BuildMaxHeap(A, n)
BEGIN
  FOR i <- floor(n/2) TO 1 STEP -1 DO
  BEGIN
    CALL MaxHeapify(A, i, n);
  END
END

PROCEDURE HeapSort(A, n)
BEGIN
  CALL BuildMaxHeap(A, n);
  FOR i <- n TO 2 STEP -1 DO
  BEGIN
    temp <- A[1];
    A[1] <- A[i];
    A[i] <- temp;
    CALL MaxHeapify(A, 1, i - 1);
  END
END`
    },
    {
      name: 'Linear Search',
      id: 'linearSearch',
      code: `PROCEDURE LinearSearch(A, n, x)
BEGIN
  FOR i <- 1 TO n DO
  BEGIN
    IF A[i] = x THEN
      RETURN i;
    ENDIF
  END
  RETURN 0;
END`
    },
    {
      name: 'Binary Search',
      id: 'binarySearch',
      code: `PROCEDURE BinarySearch(A, n, x)
BEGIN
  low <- 1;
  high <- n;
  WHILE low <= high DO
  BEGIN
    mid <- floor((low + high) / 2);
    IF A[mid] = x THEN
      RETURN mid;
    ELSE
      IF A[mid] < x THEN
        low <- mid + 1;
      ELSE
        high <- mid - 1;
      ENDIF
    ENDIF
  END
  RETURN 0;
END`
    },
    {
      name: 'Factorial (Iterative)',
      id: 'factorialIterative',
      code: `PROCEDURE FactorialIterative(n)
BEGIN
  result <- 1;
  FOR i <- 1 TO n DO
  BEGIN
    result <- result * i;
  END
  RETURN result;
END`
    },
    {
      name: 'Factorial (Recursive)',
      id: 'factorialRecursive',
      code: `PROCEDURE FactorialRecursive(n)
BEGIN
  IF n = 0 THEN
    RETURN 1;
  ELSE
    RETURN n * FactorialRecursive(n - 1);
  ENDIF
END`
    },
    {
      name: 'Fibonacci (Iterative)',
      id: 'fibonacciIterative',
      code: `PROCEDURE FibonacciIterative(n)
BEGIN
  IF n <= 1 THEN RETURN n;
  ENDIF
  a <- 0;
  b <- 1;
  FOR i <- 2 TO n DO
  BEGIN
    temp <- a + b;
    a <- b;
    b <- temp;
  END
  RETURN b;
END`
    },
    {
      name: 'Fibonacci (Recursive)',
      id: 'fibonacciRecursive',
      code: `PROCEDURE FibonacciRecursive(n)
BEGIN
  IF n <= 1 THEN
    RETURN n;
  ELSE
    RETURN FibonacciRecursive(n-1) + FibonacciRecursive(n-2);
  ENDIF
END`
    },
    {
      name: 'Matrix Multiplication',
      id: 'matrixMult',
      code: `PROCEDURE MatrixMultiply(A, B, n)
BEGIN
  FOR i <- 1 TO n DO
  BEGIN
    FOR j <- 1 TO n DO
    BEGIN
      C[i][j] <- 0;
      FOR k <- 1 TO n DO
      BEGIN
        C[i][j] <- C[i][j] + A[i][k] * B[k][j];
      END
    END
  END
END`
    },
    {
      name: 'GCD (Euclidean)',
      id: 'gcd',
      code: `PROCEDURE GCD(a, b)
BEGIN
  WHILE b > 0 DO
  BEGIN
    temp <- b;
    b <- a mod b;
    a <- temp;
  END
  RETURN a;
END`
    },
    {
      name: 'Prime Check (Naive)',
      id: 'primeCheck',
      code: `PROCEDURE IsPrime(n)
BEGIN
  IF n <= 1 THEN RETURN FALSE;
  ENDIF
  FOR i <- 2 TO floor(sqrt(n)) DO
  BEGIN
    IF n mod i = 0 THEN
      RETURN FALSE;
    ENDIF
  END
  RETURN TRUE;
END`
    },
    {
      name: 'Power (Iterative)',
      id: 'powerIterative',
      code: `PROCEDURE PowerIterative(x, n)
BEGIN
  result <- 1;
  FOR i <- 1 TO n DO
  BEGIN
    result <- result * x;
  END
  RETURN result;
END`
    },
    {
      name: 'Power (Recursive)',
      id: 'powerRecursive',
      code: `PROCEDURE PowerRecursive(x, n)
BEGIN
  IF n = 0 THEN
    RETURN 1;
  ELSE
    RETURN x * PowerRecursive(x, n - 1);
  ENDIF
END`
    },
    {
      name: 'Sum Array (Iterative)',
      id: 'sumArrayIterative',
      code: `PROCEDURE SumArrayIterative(A, n)
BEGIN
  sum <- 0;
  FOR i <- 1 TO n DO
  BEGIN
    sum <- sum + A[i];
  END
  RETURN sum;
END`
    },
    {
      name: 'Sum Array (Recursive)',
      id: 'sumArrayRecursive',
      code: `PROCEDURE SumArrayRecursive(A, n)
BEGIN
  IF n = 0 THEN
    RETURN 0;
  ELSE
    RETURN SumArrayRecursive(A, n - 1) + A[n];
  ENDIF
END`
    },
    {
      name: 'Tower of Hanoi',
      id: 'hanoi',
      code: `PROCEDURE Hanoi(n, source, target, auxiliary)
BEGIN
  IF n > 0 THEN
  BEGIN
    CALL Hanoi(n - 1, source, auxiliary, target);
    CALL MoveDisk(source, target);
    CALL Hanoi(n - 1, auxiliary, target, source);
  END
  ENDIF
END`
    }
  ]

  return (
    <div className="w-64 bg-[#0d1117] border-r border-slate-800 flex flex-col h-full">
      <div className="p-4 border-b border-slate-800 flex items-center gap-3">
        <Terminal size={20} className="text-emerald-500" />
        <span className="font-bold text-slate-200 tracking-wide">ALGO.ANALYZER</span>
      </div>
      
      <div className="p-3">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 px-3">Examples</h3>
        <div className="space-y-1">
          {algorithms.map((algo) => (
            <button
              key={algo.id}
              onClick={() => onSelectAlgorithm(algo.code)}
              className={clsx(
                "w-full text-left px-3 py-2 rounded text-sm font-mono transition-colors flex items-center gap-3",
                selectedAlgorithm === algo.code 
                  ? "bg-slate-800 text-emerald-400" 
                  : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
              )}
            >
              <FileCode size={14} className={selectedAlgorithm === algo.code ? "text-emerald-500" : "text-slate-600"} />
              {algo.name}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-auto p-4 border-t border-slate-800">
        <div className="text-xs text-slate-600 font-mono text-center">
          v1.0.0 • Ready
        </div>
      </div>
    </div>
  )
}
