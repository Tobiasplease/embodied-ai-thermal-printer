"""
Thermal Printer Integration for Embodied AI v2
Prints every subtitle with rhythmic, syllable-based timing patterns
"""

import threading
import queue
import time
import logging
from typing import Optional

try:
    from thermal_printer import DiagonalTiltedPrinter
    THERMAL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Thermal printer not available: {e}")
    THERMAL_AVAILABLE = False

class ThermalSubtitlePrinter:
    """Handles thermal printing of AI subtitles with rhythmic timing"""
    
    def __init__(self, enabled=True):
        self.enabled = enabled and THERMAL_AVAILABLE
        self.printer = None
        self.print_queue = queue.Queue()
        self.print_thread = None
        self.running = False
        self.connected = False
        
        if self.enabled:
            self._initialize_printer()
    
    def _initialize_printer(self):
        """Initialize and connect to thermal printer"""
        try:
            self.printer = DiagonalTiltedPrinter()
            # Import printer name from config if available
            try:
                from config import THERMAL_PRINTER_NAME
                printer_name = THERMAL_PRINTER_NAME
            except ImportError:
                printer_name = "XP-80"  # Default fallback
            
            self.connected = self.printer.connect(printer_name)
            if self.connected:
                print("🖨️ Thermal printer connected and ready for subtitles")
            else:
                print("⚠️ Thermal printer connection failed")
                self.enabled = False
        except Exception as e:
            print(f"⚠️ Thermal printer initialization error: {e}")
            self.enabled = False
            self.connected = False
    
    def start(self):
        """Start the thermal printing thread"""
        if not self.enabled:
            print("📝 Thermal printing disabled - subtitles will display only on screen")
            return
            
        self.running = True
        self.print_thread = threading.Thread(target=self._print_worker, daemon=True)
        self.print_thread.start()
        print("🖨️ Thermal subtitle printer thread started")
    
    def stop(self):
        """Stop the thermal printing thread"""
        self.running = False
        if self.print_thread:
            self.print_thread.join(timeout=2.0)
        if self.printer and self.connected:
            self.printer.close()
            print("🖨️ Thermal printer disconnected")
    
    def print_subtitle(self, subtitle_text: str):
        """Queue a subtitle for thermal printing with rhythmic timing"""
        if not self.enabled or not self.connected:
            return
            
        if not subtitle_text or not subtitle_text.strip():
            return
            
        # Add timestamp and queue for printing
        timestamp = time.strftime("%H:%M:%S")
        print_item = {
            'text': subtitle_text.strip(),
            'timestamp': timestamp,
            'type': 'subtitle'
        }
        
        try:
            self.print_queue.put_nowait(print_item)
            print(f"📝 Queued for thermal print: '{subtitle_text[:30]}{'...' if len(subtitle_text) > 30 else ''}'")
        except queue.Full:
            print("⚠️ Thermal print queue full - skipping subtitle")
    
    def _print_worker(self):
        """Worker thread that handles the actual thermal printing"""
        print("🖨️ Thermal print worker thread active")
        
        while self.running:
            try:
                # Wait for next print job
                print_item = self.print_queue.get(timeout=1.0)
                
                if print_item['type'] == 'subtitle':
                    self._print_subtitle_rhythmic(print_item)
                
                self.print_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"🖨️ Thermal print error: {e}")
                # Try to reconnect if connection lost
                if not self._check_connection():
                    self._attempt_reconnection()
    
    def _print_subtitle_rhythmic(self, print_item):
        """Print subtitle with rhythmic, syllable-based timing"""
        text = print_item['text']
        timestamp = print_item['timestamp']
        
        print(f"🖨️ Thermal printing: [{timestamp}] {text}")
        
        try:
            # Print with rhythmic diagonal burst (no timestamp header)
            self.printer.syllable_diagonal_burst(text)
            
        except Exception as e:
            print(f"🖨️ Error printing subtitle: {e}")
    
    def _check_connection(self) -> bool:
        """Check if printer connection is still active"""
        try:
            if not self.printer or not self.connected:
                return False
            # Simple test - try to send empty command
            self.printer.send_text("")
            return True
        except:
            self.connected = False
            return False
    
    def _attempt_reconnection(self):
        """Try to reconnect to thermal printer"""
        print("🖨️ Attempting thermal printer reconnection...")
        try:
            if self.printer:
                self.printer.close()
            
            self.printer = DiagonalTiltedPrinter()
            self.connected = self.printer.connect()
            
            if self.connected:
                print("🖨️ Thermal printer reconnected successfully")
            else:
                print("⚠️ Thermal printer reconnection failed")
                
        except Exception as e:
            print(f"⚠️ Reconnection error: {e}")
            self.connected = False


class MockThermalPrinter:
    """Mock thermal printer for testing when hardware not available"""
    
    def __init__(self):
        self.enabled = False
        self.connected = False
    
    def start(self):
        print("📝 Mock thermal printer - subtitles will show in console only")
    
    def stop(self):
        pass
    
    def print_subtitle(self, subtitle_text: str):
        print(f"🖨️ [MOCK THERMAL] {subtitle_text}")


# Factory function to create appropriate printer
def create_thermal_printer(enabled: bool = True) -> ThermalSubtitlePrinter:
    """Create thermal printer instance with fallback to mock if needed"""
    if enabled and THERMAL_AVAILABLE:
        return ThermalSubtitlePrinter(enabled=True)
    else:
        return MockThermalPrinter()