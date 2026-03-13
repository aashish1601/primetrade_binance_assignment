"""
Input validation for trading bot parameters.
Validates symbols, order types, quantities, and prices.
"""

import re
from typing import Optional
from decimal import Decimal, InvalidOperation


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_symbol(symbol: str) -> str:
    """
    Validate trading symbol format.
    
    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT)
    
    Returns:
        Validated and uppercased symbol
    
    Raises:
        ValidationError: If symbol format is invalid
    """
    if not symbol:
        raise ValidationError("Symbol cannot be empty")
    
    symbol = symbol.upper().strip()
    
    # Basic format check: letters only, minimum 5 chars (e.g., BTCUSDT)
    if not re.match(r'^[A-Z]{5,}$', symbol):
        raise ValidationError(
            f"Invalid symbol format: '{symbol}'. "
            "Expected format like 'BTCUSDT' (letters only, min 5 chars)"
        )
    
    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side.
    
    Args:
        side: Order side (BUY or SELL)
    
    Returns:
        Validated and uppercased side
    
    Raises:
        ValidationError: If side is not BUY or SELL
    """
    if not side:
        raise ValidationError("Side cannot be empty")
    
    side = side.upper().strip()
    
    if side not in ("BUY", "SELL"):
        raise ValidationError(
            f"Invalid side: '{side}'. Must be 'BUY' or 'SELL'"
        )
    
    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate order type.
    
    Args:
        order_type: Type of order (MARKET, LIMIT, STOP_LIMIT)
    
    Returns:
        Validated and uppercased order type
    
    Raises:
        ValidationError: If order type is invalid
    """
    if not order_type:
        raise ValidationError("Order type cannot be empty")
    
    order_type = order_type.upper().strip()
    
    # Replace hyphens/underscores for flexibility
    order_type = order_type.replace("-", "_")
    
    valid_types = ("MARKET", "LIMIT", "STOP", "STOP_MARKET")
    
    if order_type not in valid_types:
        raise ValidationError(
            f"Invalid order type: '{order_type}'. "
            f"Must be one of: {', '.join(valid_types)}"
        )
    
    return order_type


def validate_quantity(quantity: str) -> Decimal:
    """
    Validate order quantity.
    
    Args:
        quantity: Order quantity as string
    
    Returns:
        Validated quantity as Decimal
    
    Raises:
        ValidationError: If quantity is invalid
    """
    if not quantity:
        raise ValidationError("Quantity cannot be empty")
    
    try:
        qty = Decimal(str(quantity).strip())
    except InvalidOperation:
        raise ValidationError(
            f"Invalid quantity: '{quantity}'. Must be a valid number"
        )
    
    if qty <= 0:
        raise ValidationError(
            f"Invalid quantity: {qty}. Must be greater than 0"
        )
    
    return qty


def validate_price(price: Optional[str], order_type: str) -> Optional[Decimal]:
    """
    Validate order price.
    
    Args:
        price: Order price as string (required for LIMIT orders)
        order_type: Type of order
    
    Returns:
        Validated price as Decimal or None for MARKET orders
    
    Raises:
        ValidationError: If price is invalid or missing for LIMIT orders
    """
    requires_price = order_type in ("LIMIT", "STOP")
    
    if requires_price:
        if not price:
            raise ValidationError(
                f"Price is required for {order_type} orders"
            )
        
        try:
            p = Decimal(str(price).strip())
        except InvalidOperation:
            raise ValidationError(
                f"Invalid price: '{price}'. Must be a valid number"
            )
        
        if p <= 0:
            raise ValidationError(
                f"Invalid price: {p}. Must be greater than 0"
            )
        
        return p
    
    return None


def validate_stop_price(stop_price: Optional[str], order_type: str) -> Optional[Decimal]:
    """
    Validate stop price for stop orders.
    
    Args:
        stop_price: Stop price as string
        order_type: Type of order
    
    Returns:
        Validated stop price as Decimal or None
    
    Raises:
        ValidationError: If stop price is invalid
    """
    requires_stop = order_type in ("STOP", "STOP_MARKET")
    
    if requires_stop:
        if not stop_price:
            raise ValidationError(
                f"Stop price is required for {order_type} orders"
            )
        
        try:
            sp = Decimal(str(stop_price).strip())
        except InvalidOperation:
            raise ValidationError(
                f"Invalid stop price: '{stop_price}'. Must be a valid number"
            )
        
        if sp <= 0:
            raise ValidationError(
                f"Invalid stop price: {sp}. Must be greater than 0"
            )
        
        return sp
    
    return None


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None
) -> dict:
    """
    Validate all order parameters at once.
    
    Args:
        symbol: Trading pair symbol
        side: Order side (BUY/SELL)
        order_type: Order type (MARKET/LIMIT/STOP/STOP_MARKET)
        quantity: Order quantity
        price: Order price (required for LIMIT/STOP)
        stop_price: Stop trigger price (required for STOP/STOP_MARKET)
    
    Returns:
        Dictionary with validated parameters
    
    Raises:
        ValidationError: If any parameter is invalid
    """
    validated_type = validate_order_type(order_type)
    
    return {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validated_type,
        "quantity": validate_quantity(quantity),
        "price": validate_price(price, validated_type),
        "stop_price": validate_stop_price(stop_price, validated_type),
    }
