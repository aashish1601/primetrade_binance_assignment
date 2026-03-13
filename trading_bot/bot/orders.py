"""
Order placement logic for the trading bot.
Handles order creation, validation, and response formatting.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional

from .client import BinanceClient, BinanceAPIError
from .validators import validate_order_params, ValidationError
from .logging_config import get_logger


@dataclass
class OrderResult:
    """Represents the result of an order placement."""
    success: bool
    order_id: Optional[int] = None
    symbol: Optional[str] = None
    side: Optional[str] = None
    order_type: Optional[str] = None
    status: Optional[str] = None
    quantity: Optional[str] = None
    executed_qty: Optional[str] = None
    price: Optional[str] = None
    avg_price: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side,
            "order_type": self.order_type,
            "status": self.status,
            "quantity": self.quantity,
            "executed_qty": self.executed_qty,
            "price": self.price,
            "avg_price": self.avg_price,
            "error_message": self.error_message,
        }


class OrderManager:
    """
    Manages order placement and tracking.
    
    Provides high-level order operations with validation and logging.
    """
    
    def __init__(self, client: BinanceClient):
        """
        Initialize the order manager.
        
        Args:
            client: Configured BinanceClient instance
        """
        self.client = client
        self.logger = get_logger()
    
    def _parse_order_response(self, response: Dict[str, Any]) -> OrderResult:
        """
        Parse order API response into OrderResult.
        
        Args:
            response: Raw API response dictionary
        
        Returns:
            Parsed OrderResult
        """
        return OrderResult(
            success=True,
            order_id=response.get("orderId"),
            symbol=response.get("symbol"),
            side=response.get("side"),
            order_type=response.get("type"),
            status=response.get("status"),
            quantity=response.get("origQty"),
            executed_qty=response.get("executedQty"),
            price=response.get("price"),
            avg_price=response.get("avgPrice"),
            raw_response=response
        )
    
    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: str
    ) -> OrderResult:
        """
        Place a market order.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            side: Order side (BUY or SELL)
            quantity: Order quantity
        
        Returns:
            OrderResult with order details
        """
        self.logger.info(f"Processing MARKET order: {side} {quantity} {symbol}")
        
        try:
            # Validate inputs
            validated = validate_order_params(
                symbol=symbol,
                side=side,
                order_type="MARKET",
                quantity=quantity
            )
            
            # Place order
            response = self.client.place_order(
                symbol=validated["symbol"],
                side=validated["side"],
                order_type="MARKET",
                quantity=str(validated["quantity"])
            )
            
            result = self._parse_order_response(response)
            self.logger.info(
                f"MARKET order placed successfully: "
                f"ID={result.order_id}, Status={result.status}"
            )
            return result
            
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            return OrderResult(success=False, error_message=str(e))
        except BinanceAPIError as e:
            self.logger.error(f"API error placing market order: {e}")
            return OrderResult(success=False, error_message=str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error placing market order: {e}")
            return OrderResult(success=False, error_message=f"Unexpected error: {e}")
    
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: str,
        price: str,
        time_in_force: str = "GTC"
    ) -> OrderResult:
        """
        Place a limit order.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            side: Order side (BUY or SELL)
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force (GTC, IOC, FOK)
        
        Returns:
            OrderResult with order details
        """
        self.logger.info(
            f"Processing LIMIT order: {side} {quantity} {symbol} @ {price}"
        )
        
        try:
            # Validate inputs
            validated = validate_order_params(
                symbol=symbol,
                side=side,
                order_type="LIMIT",
                quantity=quantity,
                price=price
            )
            
            # Place order
            response = self.client.place_order(
                symbol=validated["symbol"],
                side=validated["side"],
                order_type="LIMIT",
                quantity=str(validated["quantity"]),
                price=str(validated["price"]),
                time_in_force=time_in_force
            )
            
            result = self._parse_order_response(response)
            self.logger.info(
                f"LIMIT order placed successfully: "
                f"ID={result.order_id}, Status={result.status}"
            )
            return result
            
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            return OrderResult(success=False, error_message=str(e))
        except BinanceAPIError as e:
            self.logger.error(f"API error placing limit order: {e}")
            return OrderResult(success=False, error_message=str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error placing limit order: {e}")
            return OrderResult(success=False, error_message=f"Unexpected error: {e}")
    
    def place_stop_market_order(
        self,
        symbol: str,
        side: str,
        quantity: str,
        stop_price: str
    ) -> OrderResult:
        """
        Place a stop market order.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            side: Order side (BUY or SELL)
            quantity: Order quantity
            stop_price: Stop trigger price
        
        Returns:
            OrderResult with order details
        """
        self.logger.info(
            f"Processing STOP_MARKET order: {side} {quantity} {symbol} "
            f"(stop @ {stop_price})"
        )
        
        try:
            # Validate inputs
            validated = validate_order_params(
                symbol=symbol,
                side=side,
                order_type="STOP_MARKET",
                quantity=quantity,
                stop_price=stop_price
            )
            
            # Place order
            response = self.client.place_order(
                symbol=validated["symbol"],
                side=validated["side"],
                order_type="STOP_MARKET",
                quantity=str(validated["quantity"]),
                stop_price=str(validated["stop_price"])
            )
            
            result = self._parse_order_response(response)
            self.logger.info(
                f"STOP_MARKET order placed successfully: "
                f"ID={result.order_id}, Status={result.status}"
            )
            return result
            
        except ValidationError as e:
            self.logger.error(f"Validation error: {e}")
            return OrderResult(success=False, error_message=str(e))
        except BinanceAPIError as e:
            self.logger.error(f"API error placing stop market order: {e}")
            return OrderResult(success=False, error_message=str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error placing stop market order: {e}")
            return OrderResult(success=False, error_message=f"Unexpected error: {e}")
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
        stop_price: Optional[str] = None,
        time_in_force: str = "GTC"
    ) -> OrderResult:
        """
        Place an order of any supported type.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            side: Order side (BUY or SELL)
            order_type: Order type (MARKET, LIMIT, STOP_MARKET)
            quantity: Order quantity
            price: Limit price (required for LIMIT orders)
            stop_price: Stop trigger price (required for STOP orders)
            time_in_force: Time in force (GTC, IOC, FOK)
        
        Returns:
            OrderResult with order details
        """
        order_type = order_type.upper().replace("-", "_")
        
        if order_type == "MARKET":
            return self.place_market_order(symbol, side, quantity)
        elif order_type == "LIMIT":
            if not price:
                return OrderResult(
                    success=False,
                    error_message="Price is required for LIMIT orders"
                )
            return self.place_limit_order(symbol, side, quantity, price, time_in_force)
        elif order_type == "STOP_MARKET":
            if not stop_price:
                return OrderResult(
                    success=False,
                    error_message="Stop price is required for STOP_MARKET orders"
                )
            return self.place_stop_market_order(symbol, side, quantity, stop_price)
        else:
            return OrderResult(
                success=False,
                error_message=f"Unsupported order type: {order_type}"
            )
    
    def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """
        Get current market price for a symbol.
        
        Args:
            symbol: Trading pair symbol
        
        Returns:
            Current price as Decimal or None if error
        """
        try:
            response = self.client.get_symbol_price(symbol.upper())
            return Decimal(response["price"])
        except Exception as e:
            self.logger.error(f"Error fetching price for {symbol}: {e}")
            return None
