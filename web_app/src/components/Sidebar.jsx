import React from 'react'
import { BookOpen, Code2, ChevronRight, Calculator } from 'lucide-react'
import clsx from 'clsx'

export function Sidebar({ onSelectAlgorithm, selectedAlgorithm }) {
  const algorithms = [
    {
      name: 'Insertion Sort',
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
      name: 'Merge Sort',
      code: `PROCEDURE MergeSort(A, p, r)
BEGIN
  IF p < r THEN
  BEGIN
    q <- floor((p + r) / 2);
    MergeSort(A, p, q);
    MergeSort(A, q + 1, r);
    Merge(A, p, q, r);
  END
END`
    },
    {
      name: 'Binary Search',
      code: `PROCEDURE BinarySearch(A, x)
BEGIN
  low <- 1;
  high <- length(A);
  WHILE low <= high DO
  BEGIN
    mid <- floor((low + high) / 2);
    IF A[mid] < x THEN
      low <- mid + 1
    ELSE IF A[mid] > x THEN
      high <- mid - 1
    ELSE
      RETURN mid;
  END
  RETURN 0;
END`
    },
    {
      name: 'Fibonacci (Recursive)',
      code: `PROCEDURE Fibonacci(n)
BEGIN
  IF n <= 1 THEN
    RETURN n;
  ELSE
    RETURN Fibonacci(n - 1) + Fibonacci(n - 2);
END`
    },
    {
      name: 'Bubble Sort',
      code: `PROCEDURE BubbleSort(A, n)
BEGIN
  FOR i <- 1 TO n - 1 DO
  BEGIN
    FOR j <- 1 TO n - i DO
    BEGIN
      IF A[j] > A[j+1] THEN
      BEGIN
        temp <- A[j];
        A[j] <- A[j+1];
        A[j+1] <- temp;
      END
    END
  END
END`
    },
    {
      name: 'Quick Sort',
      code: `PROCEDURE QuickSort(A, low, high)
BEGIN
  IF low < high THEN
  BEGIN
    pivot <- A[high];
    i <- low - 1;
    FOR j <- low TO high - 1 DO
    BEGIN
      IF A[j] <= pivot THEN
      BEGIN
        i <- i + 1;
        temp <- A[i];
        A[i] <- A[j];
        A[j] <- temp;
      END
    END
    temp <- A[i+1];
    A[i+1] <- A[high];
    A[high] <- temp;
    pi <- i + 1;
    QuickSort(A, low, pi - 1);
    QuickSort(A, pi + 1, high);
  END
END`
    },
    {
      name: 'Selection Sort',
      code: `PROCEDURE SelectionSort(A, n)
BEGIN
  FOR i <- 1 TO n - 1 DO
  BEGIN
    min_idx <- i;
    FOR j <- i + 1 TO n DO
    BEGIN
      IF A[j] < A[min_idx] THEN
        min_idx <- j;
    END
    temp <- A[min_idx];
    A[min_idx] <- A[i];
    A[i] <- temp;
  END
END`
    }
  ]

  return (
    <aside className="w-64 border-r border-slate-800 bg-[#0d1117] flex flex-col">
      <div className="h-14 border-b border-slate-800 flex items-center px-6 gap-2">
        <Calculator className="text-emerald-500" size={20} />
        <h1 className="font-bold text-slate-200 tracking-tight text-sm">Complexity<span className="text-emerald-500">Analyzer</span></h1>
      </div>

      <div className="p-4">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 px-2 flex items-center gap-2">
          <BookOpen size={12} /> Examples
        </h3>
        <div className="space-y-1">
          {algorithms.map((algo) => (
            <button
              key={algo.name}
              onClick={() => onSelectAlgorithm(algo.code)}
              className={clsx(
                "w-full text-left px-3 py-2 rounded text-xs font-medium transition-all flex items-center justify-between group",
                selectedAlgorithm === algo.code
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              )}
            >
              <span className="flex items-center gap-2">
                <Code2 size={14} className={selectedAlgorithm === algo.code ? "text-emerald-500" : "text-slate-600 group-hover:text-slate-500"} />
                {algo.name}
              </span>
              {selectedAlgorithm === algo.code && <ChevronRight size={12} />}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-auto p-4 border-t border-slate-800">
        <div className="bg-slate-800/50 rounded p-3">
          <p className="text-[10px] text-slate-500 leading-relaxed">
            Select an algorithm or write your own pseudo-code to analyze its time complexity.
          </p>
        </div>
      </div>
    </aside>
  )
}
