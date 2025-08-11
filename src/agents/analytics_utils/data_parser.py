"""
Data Parser for Analytics
==========================

Parses specific data values from natural language requests.
Extracts numbers, percentages, and monetary values.

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParsedDataPoint:
    """Parsed data point from text."""
    label: str
    value: float
    unit: Optional[str] = None
    is_percentage: bool = False


class DataParser:
    """
    Parses specific data values from natural language.
    Extracts structured data from user requests.
    """
    
    def __init__(self):
        """Initialize the data parser."""
        # Patterns for different data formats
        self.patterns = {
            # Q1=$1.2M, Q2=$1.5M format
            'quarter_money': re.compile(
                r'(Q[1-4])\s*[=:]\s*\$?([\d.,]+)\s*([KMB])?',
                re.IGNORECASE
            ),
            # Mon 12, Tue 15, Wed 18 format (day names with values)
            'day_value': re.compile(
                r'(Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)'
                r'\s+([\d.,]+)\s*([KMB])?',
                re.IGNORECASE
            ),
            # Jan $45K, Feb $52K format (space separator)
            'month_space_value': re.compile(
                r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
                r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
                r'\s+\$?([\d.,]+)\s*([KMB])?',
                re.IGNORECASE
            ),
            # January: 100k, February: 150k format
            'month_value': re.compile(
                r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
                r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
                r'\s*[=:]\s*\$?([\d.,]+)\s*([KMB])?',
                re.IGNORECASE
            ),
            # Company A 35%, Company B 28% format
            'label_percentage': re.compile(
                r'([A-Za-z][A-Za-z0-9\s&]+?)\s+([\d.]+)%',
                re.IGNORECASE
            ),
            # Product A: $2.5M format
            'label_money': re.compile(
                r'([A-Za-z][A-Za-z0-9\s&]+?)\s*[=:]\s*\$?([\d.,]+)\s*([KMB])?',
                re.IGNORECASE
            ),
            # Category $450K format (no colon after label)
            'category_value': re.compile(
                r'([A-Za-z][A-Za-z0-9\s&]+?)\s+\$?([\d.,]+)\s*([KMB])',
                re.IGNORECASE
            ),
            # 100, 120, 140, 160 format (comma-separated numbers)
            'comma_numbers': re.compile(
                r'(?:^|[\s:])(\d+(?:\.\d+)?)\s*(?:,|$)',
                re.IGNORECASE
            ),
            # Month 1: 10k visits format
            'generic_label': re.compile(
                r'((?:Month|Week|Day|Period|Year)\s*\d+)\s*[=:]\s*([\d.,]+)\s*([KMBk])?',
                re.IGNORECASE
            ),
            # Skills with scores: Communication 85
            'skill_score': re.compile(
                r'([A-Za-z][A-Za-z\s]+?)\s+([\d.]+)(?:/\d+|%)?',
                re.IGNORECASE
            )
        }
        
        # Day name mapping
        self.day_map = {
            'mon': 'Mon', 'monday': 'Mon',
            'tue': 'Tue', 'tuesday': 'Tue',
            'wed': 'Wed', 'wednesday': 'Wed',
            'thu': 'Thu', 'thursday': 'Thu',
            'fri': 'Fri', 'friday': 'Fri',
            'sat': 'Sat', 'saturday': 'Sat',
            'sun': 'Sun', 'sunday': 'Sun'
        }
        
        # Month name mapping
        self.month_map = {
            'jan': 'Jan', 'january': 'Jan',
            'feb': 'Feb', 'february': 'Feb',
            'mar': 'Mar', 'march': 'Mar',
            'apr': 'Apr', 'april': 'Apr',
            'may': 'May',
            'jun': 'Jun', 'june': 'Jun',
            'jul': 'Jul', 'july': 'Jul',
            'aug': 'Aug', 'august': 'Aug',
            'sep': 'Sep', 'september': 'Sep',
            'oct': 'Oct', 'october': 'Oct',
            'nov': 'Nov', 'november': 'Nov',
            'dec': 'Dec', 'december': 'Dec'
        }
    
    def _parse_number_with_unit(self, value_str: str, unit_str: Optional[str]) -> float:
        """
        Parse number with optional unit (K, M, B).
        
        Args:
            value_str: Number string
            unit_str: Optional unit (K, M, B)
            
        Returns:
            Parsed float value
        """
        # Remove commas and parse
        value = float(value_str.replace(',', ''))
        
        # Apply unit multiplier
        if unit_str:
            unit = unit_str.upper()
            if unit == 'K':
                value *= 1000
            elif unit == 'M':
                value *= 1000000
            elif unit == 'B':
                value *= 1000000000
        
        return value
    
    def parse_data_points(self, text: str) -> List[ParsedDataPoint]:
        """
        Parse data points from natural language text.
        
        Args:
            text: Input text containing data
            
        Returns:
            List of parsed data points
        """
        data_points = []
        text_lower = text.lower()
        
        # Try different patterns in order of specificity
        
        # 1. Check for day data (Mon, Tue, Wed, etc.)
        if any(day in text_lower for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']):
            day_matches = self.patterns['day_value'].findall(text)
            if day_matches:
                for day, value, unit in day_matches:
                    day_label = self.day_map.get(day.lower(), day[:3].capitalize())
                    parsed_value = self._parse_number_with_unit(value, unit)
                    data_points.append(ParsedDataPoint(
                        label=day_label,
                        value=parsed_value,
                        unit='$' if '$' in text else None
                    ))
                if data_points:
                    logger.debug(f"Parsed daily data: {len(data_points)} points")
                    return data_points
        
        # 2. Check for quarterly data with money
        if 'q1' in text_lower or 'q2' in text_lower or 'q3' in text_lower or 'q4' in text_lower:
            matches = self.patterns['quarter_money'].findall(text)
            if matches:
                for quarter, value, unit in matches:
                    parsed_value = self._parse_number_with_unit(value, unit)
                    data_points.append(ParsedDataPoint(
                        label=quarter.upper(),
                        value=parsed_value,
                        unit='$'
                    ))
                if data_points:
                    logger.debug(f"Parsed quarterly data: {len(data_points)} points")
                    return data_points
        
        # 3. Check for monthly data (with space separator first, then colon/equals)
        month_space_matches = self.patterns['month_space_value'].findall(text)
        if month_space_matches:
            for month, value, unit in month_space_matches:
                month_label = self.month_map.get(month.lower(), month.capitalize())
                parsed_value = self._parse_number_with_unit(value, unit)
                data_points.append(ParsedDataPoint(
                    label=month_label,
                    value=parsed_value,
                    unit='$' if '$' in text else None
                ))
            if data_points:
                logger.debug(f"Parsed monthly data (space format): {len(data_points)} points")
                return data_points
        
        # Try colon/equals format if space format didn't match
        month_matches = self.patterns['month_value'].findall(text)
        if month_matches:
            for month, value, unit in month_matches:
                month_label = self.month_map.get(month.lower(), month)
                parsed_value = self._parse_number_with_unit(value, unit)
                data_points.append(ParsedDataPoint(
                    label=month_label,
                    value=parsed_value,
                    unit='$' if '$' in text else None
                ))
            if data_points:
                logger.debug(f"Parsed monthly data: {len(data_points)} points")
                return data_points
        
        # 4. Check for percentage data (pie charts)
        if '%' in text:
            matches = self.patterns['label_percentage'].findall(text)
            if matches:
                for label, value in matches:
                    data_points.append(ParsedDataPoint(
                        label=label.strip(),
                        value=float(value),
                        is_percentage=True
                    ))
                if data_points:
                    logger.debug(f"Parsed percentage data: {len(data_points)} points")
                    return data_points
        
        # 5. Check for labeled money values
        if '$' in text or any(x in text_lower for x in ['million', 'billion', 'thousand']):
            # First try the category_value pattern (no colon after label)
            if 'category' in text_lower or 'sales' in text_lower:
                matches = self.patterns['category_value'].findall(text)
                if matches:
                    for label, value, unit in matches:
                        # Skip if label contains words like "by", "for", etc.
                        label_clean = label.strip()
                        if label_clean and not label_clean.lower() in ['by', 'for', 'of', 'sales', 'revenue', 'by category', 'regional sales']:
                            parsed_value = self._parse_number_with_unit(value, unit)
                            data_points.append(ParsedDataPoint(
                                label=label_clean,
                                value=parsed_value,
                                unit='$'
                            ))
                    if data_points:
                        logger.debug(f"Parsed category money data: {len(data_points)} points")
                        return data_points
            
            # Fall back to label_money pattern (with colon/equals)
            matches = self.patterns['label_money'].findall(text)
            if matches:
                for label, value, unit in matches:
                    # Skip if label is too generic
                    if label.strip() and not label.strip().isdigit():
                        parsed_value = self._parse_number_with_unit(value, unit)
                        data_points.append(ParsedDataPoint(
                            label=label.strip(),
                            value=parsed_value,
                            unit='$'
                        ))
                if data_points:
                    logger.debug(f"Parsed labeled money data: {len(data_points)} points")
                    return data_points
        
        # 6. Check for skill scores or ratings
        if any(word in text_lower for word in ['skill', 'score', 'rating', 'assessment']):
            # Look for pattern like "Communication 85"
            skill_matches = re.findall(
                r'([A-Za-z][A-Za-z\s]+?)\s+([\d.]+)(?:%|/\d+)?',
                text
            )
            if skill_matches:
                for skill, score in skill_matches:
                    skill = skill.strip()
                    # Filter out generic words
                    if skill and not skill.lower() in ['the', 'and', 'or', 'with', 'for']:
                        score_val = float(score)
                        # Normalize to 0-100 if needed
                        if '/' in text and score_val <= 5:
                            score_val = score_val * 20  # Convert 5-point to 100-point
                        data_points.append(ParsedDataPoint(
                            label=skill,
                            value=score_val,
                            is_percentage='%' in text
                        ))
                if data_points:
                    logger.debug(f"Parsed skill scores: {len(data_points)} points")
                    return data_points
        
        # 7. Check for generic labeled data
        generic_matches = self.patterns['generic_label'].findall(text)
        if generic_matches:
            for label, value, unit in generic_matches:
                parsed_value = self._parse_number_with_unit(value, unit)
                data_points.append(ParsedDataPoint(
                    label=label,
                    value=parsed_value
                ))
            if data_points:
                logger.debug(f"Parsed generic labeled data: {len(data_points)} points")
                return data_points
        
        # 8. Last resort: comma-separated numbers
        if ':' in text and ',' in text:
            # Look for pattern like "Show data: 100, 120, 140, 160"
            colon_idx = text.rfind(':')
            numbers_part = text[colon_idx+1:]
            number_matches = re.findall(r'([\d.,]+)', numbers_part)
            if number_matches:
                for i, num_str in enumerate(number_matches):
                    try:
                        value = float(num_str.replace(',', ''))
                        data_points.append(ParsedDataPoint(
                            label=f"Point {i+1}",
                            value=value
                        ))
                    except ValueError:
                        continue
                if data_points:
                    logger.debug(f"Parsed comma-separated numbers: {len(data_points)} points")
                    return data_points
        
        logger.debug("No specific data points parsed from text")
        return data_points
    
    def extract_time_period(self, text: str) -> Optional[str]:
        """
        Extract time period from text.
        
        Args:
            text: Input text
            
        Returns:
            Time period string or None
        """
        text_lower = text.lower()
        
        # Check for specific time periods
        if 'quarterly' in text_lower or 'quarter' in text_lower:
            return 'quarterly'
        elif 'monthly' in text_lower or 'month' in text_lower:
            return 'monthly'
        elif 'weekly' in text_lower or 'week' in text_lower:
            return 'weekly'
        elif 'daily' in text_lower or 'day' in text_lower:
            return 'daily'
        elif 'yearly' in text_lower or 'annual' in text_lower:
            return 'yearly'
        
        # Check for specific year mentions
        year_match = re.search(r'20\d{2}', text)
        if year_match:
            return f"year_{year_match.group()}"
        
        return None
    
    def extract_trend_preference(self, text: str) -> Optional[str]:
        """
        Extract trend preference from text.
        
        Args:
            text: Input text
            
        Returns:
            Trend type or None
        """
        text_lower = text.lower()
        
        # Check for trend indicators
        if any(word in text_lower for word in ['growth', 'increase', 'upward', 'rising']):
            return 'increasing'
        elif any(word in text_lower for word in ['decline', 'decrease', 'downward', 'falling']):
            return 'decreasing'
        elif any(word in text_lower for word in ['seasonal', 'cyclic', 'pattern']):
            return 'cyclic'
        elif any(word in text_lower for word in ['stable', 'steady', 'constant']):
            return 'stable'
        
        return None
    
    def infer_labels_for_values(self, values: List[float], context: str) -> List[str]:
        """
        Infer appropriate labels when only values are provided.
        
        Args:
            values: List of numeric values
            context: Context text
            
        Returns:
            List of inferred labels
        """
        num_values = len(values)
        context_lower = context.lower()
        
        # Quarterly data
        if num_values == 4 and any(word in context_lower for word in ['quarter', 'quarterly']):
            return ['Q1', 'Q2', 'Q3', 'Q4']
        
        # Monthly data
        elif num_values == 12 and any(word in context_lower for word in ['month', 'monthly']):
            return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Weekly data (4 weeks)
        elif num_values <= 52 and 'week' in context_lower:
            return [f"Week {i+1}" for i in range(num_values)]
        
        # Daily data (7 days)
        elif num_values == 7 and 'day' in context_lower:
            return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        # Generic categories
        elif 'category' in context_lower or 'product' in context_lower:
            if num_values <= 26:
                return [f"Category {chr(65+i)}" for i in range(num_values)]
            else:
                return [f"Item {i+1}" for i in range(num_values)]
        
        # Default to Period labels
        else:
            return [f"Period {i+1}" for i in range(num_values)]


# Example usage
if __name__ == "__main__":
    parser = DataParser()
    
    test_cases = [
        "Show quarterly sales for 2024: Q1=$1.2M, Q2=$1.5M, Q3=$1.3M, Q4=$1.8M",
        "Monthly revenue: January 100k, February 120k, March 150k",
        "Market share: Company A 35%, Company B 28%, Company C 22%, Others 15%",
        "Product sales: Electronics $2.5M, Clothing $1.8M, Home $1.2M",
        "Show data: 100, 120, 140, 160",
        "Skills: Communication 85%, Technical 75%, Leadership 90%"
    ]
    
    for test in test_cases:
        print(f"\nInput: {test}")
        points = parser.parse_data_points(test)
        for point in points:
            print(f"  {point.label}: {point.value} {point.unit or ''}")