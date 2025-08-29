"""
Performance optimizations for large-scale microsimulation.
Provides vectorized calculations and memory-efficient processing.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Callable, Any
from functools import wraps
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from memory_profiler import profile
import psutil

from .microsim import taxit, load_parameters
from .wff_microsim import famsim
from .parameters import Parameters


class PerformanceMonitor:
    """Monitor performance metrics during simulation runs."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.processing_times = {}
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.memory_usage = [psutil.virtual_memory().percent]
    
    def record_step(self, step_name: str):
        """Record timing for a processing step."""
        if self.start_time:
            self.processing_times[step_name] = time.time() - self.start_time
            self.memory_usage.append(psutil.virtual_memory().percent)
    
    def get_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        total_time = time.time() - self.start_time if self.start_time else 0
        
        return {
            "total_runtime_seconds": total_time,
            "peak_memory_percent": max(self.memory_usage) if self.memory_usage else 0,
            "step_timings": self.processing_times,
            "memory_profile": self.memory_usage
        }


def performance_timer(func):
    """Decorator to time function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} executed in {end - start:.2f} seconds")
        return result
    return wrapper


class OptimizedMicrosimulation:
    """
    Optimized microsimulation engine for large datasets.
    Uses vectorized operations and memory-efficient processing.
    """
    
    def __init__(self, chunk_size: int = 10000, use_multiprocessing: bool = False):
        self.chunk_size = chunk_size
        self.use_multiprocessing = use_multiprocessing
        self.n_cores = mp.cpu_count() - 1 if use_multiprocessing else 1
        self.monitor = PerformanceMonitor()
    
    @performance_timer
    def vectorized_tax_calculation(self, df: pd.DataFrame, 
                                  tax_params: Any) -> pd.Series:
        """
        Vectorized income tax calculation - much faster than apply().
        """
        incomes = df["taxable_income"].values
        rates = np.array(tax_params.rates)
        thresholds = np.array([0] + tax_params.thresholds)
        
        # Create tax calculation matrix
        n_brackets = len(rates)
        n_individuals = len(incomes)
        
        # Broadcast income and thresholds for vectorized calculation
        income_matrix = np.broadcast_to(incomes.reshape(-1, 1), (n_individuals, n_brackets))
        threshold_matrix = np.broadcast_to(thresholds.reshape(1, -1), (n_individuals, n_brackets))
        
        # Calculate taxable income in each bracket
        if n_brackets > 1:
            upper_thresholds = np.concatenate([thresholds[1:], [np.inf]])
            upper_matrix = np.broadcast_to(upper_thresholds.reshape(1, -1), (n_individuals, n_brackets))
            
            taxable_in_bracket = np.maximum(0, 
                np.minimum(income_matrix, upper_matrix) - threshold_matrix
            )
        else:
            taxable_in_bracket = np.maximum(0, income_matrix - threshold_matrix)
        
        # Apply rates to each bracket
        rate_matrix = np.broadcast_to(rates.reshape(1, -1), (n_individuals, n_brackets))
        tax_by_bracket = taxable_in_bracket * rate_matrix
        
        # Sum across brackets
        total_tax = np.sum(tax_by_bracket, axis=1)
        
        return pd.Series(total_tax, index=df.index)
    
    @performance_timer
    def chunked_processing(self, df: pd.DataFrame, 
                          processing_func: Callable, 
                          **func_kwargs) -> pd.DataFrame:
        """
        Process large DataFrame in chunks to manage memory.
        """
        results = []
        n_chunks = len(df) // self.chunk_size + (1 if len(df) % self.chunk_size != 0 else 0)
        
        for i in range(n_chunks):
            start_idx = i * self.chunk_size
            end_idx = min((i + 1) * self.chunk_size, len(df))
            
            chunk = df.iloc[start_idx:end_idx].copy()
            chunk_result = processing_func(chunk, **func_kwargs)
            results.append(chunk_result)
            
            # Memory cleanup
            del chunk
            
            if i % 10 == 0:  # Progress reporting
                print(f"Processed chunk {i+1}/{n_chunks} ({(i+1)/n_chunks*100:.1f}%)")
        
        return pd.concat(results, ignore_index=True)
    
    def parallel_processing(self, df: pd.DataFrame, 
                           processing_func: Callable, 
                           **func_kwargs) -> pd.DataFrame:
        """
        Process DataFrame using multiprocessing.
        """
        # Split data into chunks for parallel processing
        chunk_size = len(df) // self.n_cores
        chunks = [df.iloc[i:i + chunk_size].copy() 
                 for i in range(0, len(df), chunk_size)]
        
        results = []
        
        with ProcessPoolExecutor(max_workers=self.n_cores) as executor:
            # Submit all chunks
            future_to_chunk = {
                executor.submit(processing_func, chunk, **func_kwargs): i 
                for i, chunk in enumerate(chunks)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_chunk):
                chunk_idx = future_to_chunk[future]
                try:
                    result = future.result()
                    results.append((chunk_idx, result))
                except Exception as e:
                    print(f"Chunk {chunk_idx} failed: {e}")
                    raise
        
        # Sort by original chunk order and concatenate
        results.sort(key=lambda x: x[0])
        return pd.concat([result for _, result in results], ignore_index=True)
    
    @performance_timer
    def optimized_simulation(self, df: pd.DataFrame, 
                           year: str, 
                           parameter_overrides: Optional[Dict] = None) -> pd.DataFrame:
        """
        Run optimized microsimulation with performance monitoring.
        """
        self.monitor.start_monitoring()
        
        # Load parameters
        params = load_parameters(year)
        if parameter_overrides:
            from .optimisation import _set_nested_attr
            for path, value in parameter_overrides.items():
                _set_nested_attr(params, path, value)
        
        self.monitor.record_step("parameter_loading")
        
        # Prepare income calculation
        income_cols = [
            "employment_income", "self_employment_income", 
            "investment_income", "rental_property_income", 
            "private_pensions_annuities"
        ]
        
        # Ensure all income columns exist
        for col in income_cols:
            if col not in df.columns:
                df[col] = 0.0
        
        df["taxable_income"] = df[income_cols].sum(axis=1)
        self.monitor.record_step("income_preparation")
        
        # Choose processing method based on dataset size and settings
        if len(df) > 100000 and self.use_multiprocessing:
            print(f"Using parallel processing with {self.n_cores} cores")
            result_df = self.parallel_processing(df, self._process_chunk, params=params)
        elif len(df) > self.chunk_size:
            print(f"Using chunked processing with chunk size {self.chunk_size}")
            result_df = self.chunked_processing(df, self._process_chunk, params=params)
        else:
            print("Using standard processing")
            result_df = self._process_chunk(df, params=params)
        
        self.monitor.record_step("simulation_complete")
        
        # Add performance metadata
        perf_report = self.monitor.get_report()
        print(f"Simulation completed in {perf_report['total_runtime_seconds']:.2f} seconds")
        print(f"Peak memory usage: {perf_report['peak_memory_percent']:.1f}%")
        
        return result_df
    
    def _process_chunk(self, chunk_df: pd.DataFrame, params: Parameters) -> pd.DataFrame:
        """Process a single chunk of data."""
        result_df = chunk_df.copy()
        
        # Vectorized tax calculation
        if params.tax_brackets:
            result_df["tax_liability"] = self.vectorized_tax_calculation(
                result_df, params.tax_brackets
            )
        
        # Calculate IETC using vectorized operations
        if params.ietc:
            result_df["ietc_amount"] = self._vectorized_ietc(result_df, params.ietc)
        
        # WFF calculations (if family data available)
        if all(col in result_df.columns for col in ["FTCwgt", "IWTCwgt"]):
            # For WFF, we still need to use the existing famsim function
            # but we can optimize by processing fewer columns
            wff_cols = ["familyinc", "FTCwgt", "IWTCwgt", "BSTC0wgt", "BSTC01wgt", 
                       "BSTC1wgt", "MFTCwgt", "iwtc_elig", "pplcnt", "MFTC_total", 
                       "MFTC_elig", "sharedcare"]
            
            # Create minimal dataframe for WFF calculation
            if all(col in result_df.columns for col in wff_cols):
                wff_df = result_df[wff_cols].copy()
                wff_result = famsim(wff_df, year="2024-2025")  # Use year parameter
                
                # Merge results back
                wff_result_cols = ["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]
                for col in wff_result_cols:
                    if col in wff_result.columns:
                        result_df[col] = wff_result[col]
        
        # Calculate disposable income
        tax_liability = result_df.get("tax_liability", 0)
        wff_total = result_df[["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]].sum(axis=1) \
                   if all(col in result_df.columns for col in ["FTCcalc", "IWTCcalc", "BSTCcalc", "MFTCcalc"]) else 0
        ietc_amount = result_df.get("ietc_amount", 0)
        
        result_df["disposable_income"] = (
            result_df["taxable_income"] - tax_liability + wff_total + ietc_amount
        )
        
        return result_df
    
    def _vectorized_ietc(self, df: pd.DataFrame, ietc_params: Any) -> pd.Series:
        """Vectorized IETC calculation."""
        incomes = df["taxable_income"].values
        
        # Basic entitlement for all
        base_ietc = np.full(len(incomes), ietc_params.ent)
        
        # Apply abatement for incomes above threshold
        excess_income = np.maximum(0, incomes - ietc_params.thresh)
        abatement = excess_income * ietc_params.abate
        
        # Final IETC (cannot be negative)
        final_ietc = np.maximum(0, base_ietc - abatement)
        
        return pd.Series(final_ietc, index=df.index)


class MemoryEfficientDataLoader:
    """
    Efficient data loading for large datasets.
    """
    
    @staticmethod
    def load_large_csv(file_path: str, 
                      required_columns: Optional[List[str]] = None,
                      sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load large CSV files efficiently.
        """
        # First, read just the header to check columns
        sample_df = pd.read_csv(file_path, nrows=1)
        available_columns = sample_df.columns.tolist()
        
        # Determine which columns to load
        if required_columns:
            columns_to_load = [col for col in required_columns if col in available_columns]
            missing_columns = [col for col in required_columns if col not in available_columns]
            if missing_columns:
                print(f"Warning: Missing columns {missing_columns}")
        else:
            columns_to_load = available_columns
        
        # Load with optimizations
        dtype_optimizations = {
            'age': 'int8',
            'adults': 'int8', 
            'children': 'int8',
            'employment_income': 'float32',
            'self_employment_income': 'float32',
            'investment_income': 'float32'
        }
        
        # Apply dtype optimizations for columns that exist
        dtypes = {col: dtype for col, dtype in dtype_optimizations.items() 
                 if col in columns_to_load}
        
        # Load data
        if sample_size:
            # Random sampling for testing
            total_rows = sum(1 for _ in open(file_path)) - 1  # Exclude header
            skip_rows = np.random.choice(range(1, total_rows + 1), 
                                       size=total_rows - sample_size, 
                                       replace=False)
            df = pd.read_csv(file_path, usecols=columns_to_load, 
                           dtype=dtypes, skiprows=skip_rows)
        else:
            # Load all data in chunks to manage memory
            chunk_size = 10000
            chunks = []
            
            for chunk in pd.read_csv(file_path, usecols=columns_to_load, 
                                   dtype=dtypes, chunksize=chunk_size):
                chunks.append(chunk)
            
            df = pd.concat(chunks, ignore_index=True)
        
        return df
    
    @staticmethod
    def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize DataFrame memory usage by downcasting numeric types.
        """
        optimized_df = df.copy()
        
        # Downcast integers
        int_columns = optimized_df.select_dtypes(include=['int64']).columns
        for col in int_columns:
            optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='integer')
        
        # Downcast floats
        float_columns = optimized_df.select_dtypes(include=['float64']).columns
        for col in float_columns:
            optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
        
        # Convert object columns to category if appropriate
        object_columns = optimized_df.select_dtypes(include=['object']).columns
        for col in object_columns:
            if optimized_df[col].nunique() / len(optimized_df) < 0.5:  # Less than 50% unique values
                optimized_df[col] = optimized_df[col].astype('category')
        
        return optimized_df


def create_performance_benchmark(df: pd.DataFrame, year: str = "2024-2025") -> Dict[str, Any]:
    """
    Benchmark different processing approaches.
    """
    print("Starting performance benchmark...")
    
    # Test standard processing
    start_time = time.time()
    optimizer_standard = OptimizedMicrosimulation(use_multiprocessing=False)
    result_standard = optimizer_standard.optimized_simulation(df.copy(), year)
    standard_time = time.time() - start_time
    
    # Test chunked processing  
    start_time = time.time()
    optimizer_chunked = OptimizedMicrosimulation(chunk_size=5000, use_multiprocessing=False)
    result_chunked = optimizer_chunked.optimized_simulation(df.copy(), year)
    chunked_time = time.time() - start_time
    
    # Test parallel processing (if dataset is large enough)
    parallel_time = None
    if len(df) > 10000:
        start_time = time.time()
        optimizer_parallel = OptimizedMicrosimulation(use_multiprocessing=True)
        result_parallel = optimizer_parallel.optimized_simulation(df.copy(), year)
        parallel_time = time.time() - start_time
    
    benchmark_results = {
        "dataset_size": len(df),
        "standard_time": standard_time,
        "chunked_time": chunked_time,
        "parallel_time": parallel_time,
        "speedup_chunked": standard_time / chunked_time if chunked_time > 0 else None,
        "speedup_parallel": standard_time / parallel_time if parallel_time else None,
        "recommended_approach": "parallel" if parallel_time and parallel_time < min(standard_time, chunked_time)
                              else "chunked" if chunked_time < standard_time else "standard"
    }
    
    return benchmark_results