"""
Binance Futures Testnet API Client.
Handles authentication, request signing, and API communication.
"""

import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from .logging_config import get_logger


class BinanceAPIError(Exception):
    """Custom exception for Binance API errors."""
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error [{code}]: {message}")


class BinanceClient:
    """
    Client for interacting with Binance Futures Testnet API.
    
    Handles request signing, authentication, and error handling.
    """
    
    BASE_URL = "https://testnet.binancefuture.com"
    
    def __init__(self, api_key: str, api_secret: str, timeout: int = 30):
        """
        Initialize the Binance client.
        
        Args:
            api_key: Binance Futures Testnet API key
            api_secret: Binance Futures Testnet API secret
            timeout: Request timeout in seconds
        """
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        })
        self.logger = get_logger()
    
    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds."""
        return int(time.time() * 1000)
    
    def _sign_params(self, params: Dict[str, Any]) -> str:
        """
        Create HMAC SHA256 signature for request parameters.
        
        Args:
            params: Request parameters to sign
        
        Returns:
            Hexadecimal signature string
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = True
    ) -> Dict[str, Any]:
        """
        Make an API request to Binance.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            params: Request parameters
            signed: Whether to sign the request
        
        Returns:
            JSON response as dictionary
        
        Raises:
            BinanceAPIError: If API returns an error
            requests.RequestException: If network error occurs
        """
        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        
        if signed:
            params["timestamp"] = self._get_timestamp()
            params["signature"] = self._sign_params(params)
        
        # Log the request (mask sensitive data)
        log_params = {k: v for k, v in params.items() if k != "signature"}
        self.logger.info(f"API Request: {method} {endpoint}")
        self.logger.debug(f"Request params: {log_params}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params if method == "GET" else None,
                data=params if method in ("POST", "DELETE") else None,
                timeout=self.timeout
            )
            
            # Log response status
            self.logger.info(f"API Response: Status {response.status_code}")
            
            # Parse response
            data = response.json()
            
            # Check for API errors
            if response.status_code >= 400:
                error_code = data.get("code", response.status_code)
                error_msg = data.get("msg", "Unknown error")
                self.logger.error(f"API Error: [{error_code}] {error_msg}")
                raise BinanceAPIError(error_code, error_msg)
            
            self.logger.debug(f"Response data: {data}")
            return data
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timeout after {self.timeout}s")
            raise
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Get exchange trading rules and symbol information.
        
        Returns:
            Exchange information dictionary
        """
        return self._request("GET", "/fapi/v1/exchangeInfo", signed=False)
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get current account information.
        
        Returns:
            Account information dictionary
        """
        return self._request("GET", "/fapi/v2/account")
    
    def get_symbol_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get latest price for a symbol.
        
        Args:
            symbol: Trading pair symbol
        
        Returns:
            Price information dictionary
        """
        return self._request(
            "GET", 
            "/fapi/v1/ticker/price", 
            params={"symbol": symbol},
            signed=False
        )
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
        stop_price: Optional[str] = None,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Place a new order.
        
        Args:
            symbol: Trading pair symbol
            side: BUY or SELL
            order_type: MARKET, LIMIT, STOP, or STOP_MARKET
            quantity: Order quantity
            price: Limit price (required for LIMIT/STOP orders)
            stop_price: Stop trigger price (required for STOP/STOP_MARKET)
            time_in_force: Time in force (GTC, IOC, FOK)
        
        Returns:
            Order response dictionary
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        
        # Add price for limit orders
        if order_type in ("LIMIT", "STOP"):
            if price:
                params["price"] = price
            params["timeInForce"] = time_in_force
        
        # Add stop price for stop orders
        if order_type in ("STOP", "STOP_MARKET"):
            if stop_price:
                params["stopPrice"] = stop_price
        
        self.logger.info(
            f"Placing {order_type} {side} order: {quantity} {symbol}"
            + (f" @ {price}" if price else "")
            + (f" (stop: {stop_price})" if stop_price else "")
        )
        
        return self._request("POST", "/fapi/v1/order", params=params)
    
    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get order details by order ID.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID
        
        Returns:
            Order details dictionary
        """
        return self._request(
            "GET",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id}
        )
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an active order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID to cancel
        
        Returns:
            Cancelled order details
        """
        return self._request(
            "DELETE",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id}
        )
    
    def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """
        Get all open orders.
        
        Args:
            symbol: Optional symbol filter
        
        Returns:
            List of open orders
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._request("GET", "/fapi/v1/openOrders", params=params)
