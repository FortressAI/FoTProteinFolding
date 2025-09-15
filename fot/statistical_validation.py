#!/usr/bin/env python3
"""
Statistical Validation Suite for Publication-Quality Results

This module implements rigorous statistical validation required for 
life-saving research publication standards.

Requirements:
- Confidence intervals for all predictions
- Cross-validation on independent datasets
- Multiple testing correction
- Power analysis and effect size calculations
- False discovery rate control
"""

import numpy as np
import scipy.stats as stats
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import roc_auc_score, precision_recall_curve, matthews_corrcoef
from statsmodels.stats.power import ttest_power
from statsmodels.stats.multitest import multipletests
from typing import Dict, List, Tuple, Optional, Any
import warnings
import logging

logger = logging.getLogger(__name__)

class StatisticalValidationSuite:
    """
    Comprehensive statistical validation for therapeutic discovery
    
    Implements publication-quality statistical analysis with:
    - Bootstrap confidence intervals
    - Cross-validation frameworks
    - Multiple testing correction
    - Power analysis
    - Effect size calculations
    """
    
    def __init__(self, confidence_level: float = 0.95, 
                 fdr_threshold: float = 0.05,
                 power_threshold: float = 0.8,
                 random_seed: int = 42):
        """
        Initialize statistical validation suite
        
        Args:
            confidence_level: Confidence level for intervals (default 0.95)
            fdr_threshold: False discovery rate threshold (default 0.05)
            power_threshold: Statistical power threshold (default 0.8)
            random_seed: Random seed for reproducibility
        """
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
        self.fdr_threshold = fdr_threshold
        self.power_threshold = power_threshold
        self.random_seed = random_seed
        
        # Set random seed for reproducibility
        np.random.seed(random_seed)
        
        logger.info(f"Statistical validation initialized:")
        logger.info(f"  Confidence level: {confidence_level}")
        logger.info(f"  FDR threshold: {fdr_threshold}")
        logger.info(f"  Power threshold: {power_threshold}")
    
    def calculate_confidence_intervals(self, data: np.ndarray, 
                                     method: str = 'bootstrap',
                                     n_bootstrap: int = 10000) -> Tuple[float, float, float]:
        """
        Calculate confidence intervals for data
        
        Args:
            data: Input data array
            method: Method for CI calculation ('bootstrap', 'normal', 't')
            n_bootstrap: Number of bootstrap samples
            
        Returns:
            Tuple of (mean, lower_bound, upper_bound)
        """
        if len(data) == 0:
            raise ValueError("Cannot calculate confidence intervals for empty data")
        
        mean_val = np.mean(data)
        
        if method == 'bootstrap':
            # Bootstrap confidence intervals (manual implementation)
            bootstrap_means = []
            for _ in range(n_bootstrap):
                bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
                bootstrap_means.append(np.mean(bootstrap_sample))
            
            bootstrap_means = np.array(bootstrap_means)
            alpha = 1 - self.confidence_level
            lower_bound = np.percentile(bootstrap_means, (alpha/2) * 100)
            upper_bound = np.percentile(bootstrap_means, (1 - alpha/2) * 100)
            
        elif method == 'normal':
            # Normal approximation
            std_err = stats.sem(data)
            z_score = stats.norm.ppf(1 - self.alpha/2)
            margin = z_score * std_err
            lower_bound = mean_val - margin
            upper_bound = mean_val + margin
            
        elif method == 't':
            # t-distribution
            std_err = stats.sem(data)
            df = len(data) - 1
            t_score = stats.t.ppf(1 - self.alpha/2, df)
            margin = t_score * std_err
            lower_bound = mean_val - margin
            upper_bound = mean_val + margin
            
        else:
            raise ValueError(f"Unknown method: {method}")
        
        logger.info(f"Confidence interval ({method}): {mean_val:.4f} [{lower_bound:.4f}, {upper_bound:.4f}]")
        
        return mean_val, lower_bound, upper_bound
    
    def cross_validate_predictions(self, model, X: np.ndarray, y: np.ndarray,
                                 cv_folds: int = 5, 
                                 scoring: str = 'accuracy') -> Dict[str, Any]:
        """
        Perform k-fold cross-validation
        
        Args:
            model: Scikit-learn compatible model
            X: Feature matrix
            y: Target values
            cv_folds: Number of cross-validation folds
            scoring: Scoring metric
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Performing {cv_folds}-fold cross-validation")
        
        # K-fold cross-validation
        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=self.random_seed)
        cv_scores = cross_val_score(model, X, y, cv=kf, scoring=scoring)
        
        # Calculate statistics
        mean_score = np.mean(cv_scores)
        std_score = np.std(cv_scores)
        
        # Confidence interval for CV scores
        mean_ci, lower_ci, upper_ci = self.calculate_confidence_intervals(cv_scores)
        
        results = {
            'cv_scores': cv_scores,
            'mean_score': mean_score,
            'std_score': std_score,
            'confidence_interval': (lower_ci, upper_ci),
            'n_folds': cv_folds,
            'scoring_metric': scoring
        }
        
        logger.info(f"Cross-validation results:")
        logger.info(f"  Mean {scoring}: {mean_score:.4f} ± {std_score:.4f}")
        logger.info(f"  95% CI: [{lower_ci:.4f}, {upper_ci:.4f}]")
        
        return results
    
    def assess_statistical_power(self, effect_size: float, 
                               sample_size: int,
                               alpha: float = 0.05,
                               alternative: str = 'two-sided') -> Dict[str, float]:
        """
        Calculate statistical power for given parameters
        
        Args:
            effect_size: Cohen's d effect size
            sample_size: Sample size
            alpha: Type I error rate
            alternative: Type of test ('two-sided', 'larger', 'smaller')
            
        Returns:
            Dictionary with power analysis results
        """
        # Calculate power
        power = ttest_power(effect_size, sample_size, alpha, alternative)
        
        # Calculate minimum sample size for desired power
        from statsmodels.stats.power import ttest_power, solve_power
        min_sample_size = solve_power(effect_size, power=self.power_threshold, 
                                    alpha=alpha, alternative=alternative)
        
        results = {
            'effect_size': effect_size,
            'sample_size': sample_size,
            'alpha': alpha,
            'power': power,
            'power_adequate': power >= self.power_threshold,
            'min_sample_size': min_sample_size,
            'power_threshold': self.power_threshold
        }
        
        logger.info(f"Power analysis:")
        logger.info(f"  Effect size (Cohen's d): {effect_size:.3f}")
        logger.info(f"  Sample size: {sample_size}")
        logger.info(f"  Statistical power: {power:.3f}")
        logger.info(f"  Power adequate (≥{self.power_threshold}): {power >= self.power_threshold}")
        logger.info(f"  Min sample size needed: {min_sample_size:.0f}")
        
        return results
    
    def calculate_effect_size(self, group1: np.ndarray, group2: np.ndarray,
                            method: str = 'cohen_d') -> Dict[str, float]:
        """
        Calculate effect size between two groups
        
        Args:
            group1: First group data
            group2: Second group data
            method: Effect size method ('cohen_d', 'glass_delta', 'hedges_g')
            
        Returns:
            Dictionary with effect size results
        """
        if method == 'cohen_d':
            # Cohen's d
            pooled_std = np.sqrt(((len(group1) - 1) * np.var(group1, ddof=1) + 
                                (len(group2) - 1) * np.var(group2, ddof=1)) / 
                               (len(group1) + len(group2) - 2))
            effect_size = (np.mean(group1) - np.mean(group2)) / pooled_std
            
        elif method == 'glass_delta':
            # Glass's delta
            effect_size = (np.mean(group1) - np.mean(group2)) / np.std(group2, ddof=1)
            
        elif method == 'hedges_g':
            # Hedges' g (bias-corrected Cohen's d)
            cohen_d = self.calculate_effect_size(group1, group2, 'cohen_d')['effect_size']
            correction = 1 - (3 / (4 * (len(group1) + len(group2)) - 9))
            effect_size = cohen_d * correction
            
        else:
            raise ValueError(f"Unknown effect size method: {method}")
        
        # Effect size interpretation
        if abs(effect_size) < 0.2:
            interpretation = 'negligible'
        elif abs(effect_size) < 0.5:
            interpretation = 'small'
        elif abs(effect_size) < 0.8:
            interpretation = 'medium'
        else:
            interpretation = 'large'
        
        results = {
            'effect_size': effect_size,
            'method': method,
            'interpretation': interpretation,
            'group1_mean': np.mean(group1),
            'group2_mean': np.mean(group2),
            'group1_std': np.std(group1, ddof=1),
            'group2_std': np.std(group2, ddof=1)
        }
        
        logger.info(f"Effect size ({method}): {effect_size:.3f} ({interpretation})")
        
        return results
    
    def correct_multiple_testing(self, p_values: np.ndarray,
                                method: str = 'fdr_bh') -> Dict[str, Any]:
        """
        Apply multiple testing correction
        
        Args:
            p_values: Array of p-values
            method: Correction method ('fdr_bh', 'bonferroni', 'holm')
            
        Returns:
            Dictionary with corrected results
        """
        if method == 'fdr_bh':
            # Benjamini-Hochberg FDR correction
            rejected, p_corrected, alpha_sidak, alpha_bonf = multipletests(
                p_values, alpha=self.fdr_threshold, method='fdr_bh'
            )
        elif method == 'bonferroni':
            # Bonferroni correction
            rejected, p_corrected, alpha_sidak, alpha_bonf = multipletests(
                p_values, alpha=self.alpha, method='bonferroni'
            )
        elif method == 'holm':
            # Holm-Bonferroni correction
            rejected, p_corrected, alpha_sidak, alpha_bonf = multipletests(
                p_values, alpha=self.alpha, method='holm'
            )
        else:
            raise ValueError(f"Unknown correction method: {method}")
        
        # Calculate false discovery rate
        if np.sum(rejected) > 0:
            fdr = np.sum(p_corrected[rejected] > self.alpha) / np.sum(rejected)
        else:
            fdr = 0.0
        
        results = {
            'original_p_values': p_values,
            'corrected_p_values': p_corrected,
            'rejected': rejected,
            'num_significant': np.sum(rejected),
            'num_tests': len(p_values),
            'fdr': fdr,
            'method': method,
            'alpha_threshold': self.alpha
        }
        
        logger.info(f"Multiple testing correction ({method}):")
        logger.info(f"  Number of tests: {len(p_values)}")
        logger.info(f"  Significant results: {np.sum(rejected)} ({np.sum(rejected)/len(p_values):.1%})")
        logger.info(f"  False discovery rate: {fdr:.3f}")
        
        return results
    
    def validate_prediction_performance(self, y_true: np.ndarray, 
                                      y_pred: np.ndarray,
                                      y_prob: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Comprehensive prediction performance validation
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_prob: Predicted probabilities (optional)
            
        Returns:
            Dictionary with performance metrics
        """
        from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                                   f1_score, confusion_matrix, classification_report)
        
        # Basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')
        f1 = f1_score(y_true, y_pred, average='weighted')
        mcc = matthews_corrcoef(y_true, y_pred)
        
        results = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'matthews_correlation': mcc,
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
            'classification_report': classification_report(y_true, y_pred, output_dict=True)
        }
        
        # Add ROC AUC if probabilities provided
        if y_prob is not None:
            try:
                auc = roc_auc_score(y_true, y_prob)
                results['roc_auc'] = auc
                logger.info(f"ROC AUC: {auc:.3f}")
            except ValueError as e:
                logger.warning(f"Could not calculate ROC AUC: {e}")
        
        # Confidence intervals for metrics
        n_bootstrap = 1000
        accuracy_ci = self._bootstrap_metric(y_true, y_pred, accuracy_score, n_bootstrap)
        precision_ci = self._bootstrap_metric(y_true, y_pred, 
                                            lambda y_t, y_p: precision_score(y_t, y_p, average='weighted'), 
                                            n_bootstrap)
        
        results['confidence_intervals'] = {
            'accuracy': accuracy_ci,
            'precision': precision_ci
        }
        
        logger.info(f"Prediction performance:")
        logger.info(f"  Accuracy: {accuracy:.3f} [{accuracy_ci[0]:.3f}, {accuracy_ci[1]:.3f}]")
        logger.info(f"  Precision: {precision:.3f}")
        logger.info(f"  Recall: {recall:.3f}")
        logger.info(f"  F1-score: {f1:.3f}")
        logger.info(f"  Matthews correlation: {mcc:.3f}")
        
        return results
    
    def _bootstrap_metric(self, y_true: np.ndarray, y_pred: np.ndarray,
                         metric_func, n_bootstrap: int = 1000) -> Tuple[float, float]:
        """Calculate bootstrap confidence interval for a metric"""
        metrics = []
        n_samples = len(y_true)
        
        for _ in range(n_bootstrap):
            # Bootstrap sample
            indices = np.random.choice(n_samples, n_samples, replace=True)
            y_true_boot = y_true[indices]
            y_pred_boot = y_pred[indices]
            
            try:
                metric = metric_func(y_true_boot, y_pred_boot)
                metrics.append(metric)
            except:
                continue
        
        metrics = np.array(metrics)
        lower = np.percentile(metrics, (1 - self.confidence_level) / 2 * 100)
        upper = np.percentile(metrics, (1 + self.confidence_level) / 2 * 100)
        
        return lower, upper
    
    def validate_statistical_assumptions(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Validate statistical assumptions for parametric tests
        
        Args:
            data: Input data array
            
        Returns:
            Dictionary with assumption test results
        """
        results = {}
        
        # Normality tests
        shapiro_stat, shapiro_p = stats.shapiro(data)
        results['normality'] = {
            'shapiro_wilk_statistic': shapiro_stat,
            'shapiro_wilk_p_value': shapiro_p,
            'is_normal': shapiro_p > self.alpha
        }
        
        # Homoscedasticity (constant variance)
        # Use Levene's test if multiple groups provided
        
        logger.info(f"Statistical assumptions:")
        logger.info(f"  Normality (Shapiro-Wilk): p={shapiro_p:.4f}, normal={shapiro_p > self.alpha}")
        
        return results

def create_publication_validation_report(predictions: np.ndarray,
                                       experimental_data: np.ndarray,
                                       model=None) -> Dict[str, Any]:
    """
    Create comprehensive validation report for publication
    
    Args:
        predictions: Model predictions
        experimental_data: Experimental validation data
        model: Optional trained model for cross-validation
        
    Returns:
        Complete validation report
    """
    validator = StatisticalValidationSuite()
    
    report = {
        'timestamp': np.datetime64('now').isoformat(),
        'validation_summary': {},
        'statistical_tests': {},
        'performance_metrics': {},
        'recommendations': []
    }
    
    # Confidence intervals
    pred_mean, pred_lower, pred_upper = validator.calculate_confidence_intervals(predictions)
    exp_mean, exp_lower, exp_upper = validator.calculate_confidence_intervals(experimental_data)
    
    report['confidence_intervals'] = {
        'predictions': {'mean': pred_mean, 'ci': (pred_lower, pred_upper)},
        'experimental': {'mean': exp_mean, 'ci': (exp_lower, exp_upper)}
    }
    
    # Effect size
    effect_size_results = validator.calculate_effect_size(predictions, experimental_data)
    report['effect_size'] = effect_size_results
    
    # Correlation analysis
    correlation, p_value = stats.pearsonr(predictions, experimental_data)
    report['correlation'] = {
        'pearson_r': correlation,
        'p_value': p_value,
        'significant': p_value < 0.05
    }
    
    # Statistical power analysis
    sample_size = len(predictions)
    power_results = validator.assess_statistical_power(
        effect_size_results['effect_size'], sample_size
    )
    report['power_analysis'] = power_results
    
    # Recommendations
    if correlation < 0.8:
        report['recommendations'].append("Correlation below 0.8 - consider model improvement")
    
    if not power_results['power_adequate']:
        report['recommendations'].append(f"Statistical power inadequate - need ≥{power_results['min_sample_size']:.0f} samples")
    
    if effect_size_results['interpretation'] == 'negligible':
        report['recommendations'].append("Effect size negligible - practical significance questionable")
    
    logger.info("Publication validation report generated")
    
    return report
