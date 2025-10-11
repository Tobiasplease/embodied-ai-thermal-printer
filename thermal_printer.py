#!/usr/bin/env python3
"""
Diagonal Tilted Thermal Printer
Uses rotation commands and variable line spacing for dramatic visual effects
"""

import win32print
import time
import syllapy
import re
import random

class DiagonalTiltedPrinter:
    def __init__(self):
        self.printer_handle = None
        self.ESC = '\x1b'
        self.GS = '\x1d'
        
        # Text rotation commands
        self.ROTATE_90_ON = self.ESC + 'V\x01'     # Rotate 90 degrees
        self.ROTATE_OFF = self.ESC + 'V\x00'       # Normal orientation
        
        # Size commands
        self.DOUBLE_HEIGHT = self.GS + '!\x01'     # Double height
        self.DOUBLE_WIDTH = self.GS + '!\x10'      # Double width  
        self.DOUBLE_BOTH = self.GS + '!\x11'       # Both directions
        self.TRIPLE_HEIGHT = self.GS + '!\x02'     # Triple height
        self.QUAD_HEIGHT = self.GS + '!\x03'       # Quadruple height
        self.NORMAL_SIZE = self.GS + '!\x00'       # Reset to normal
        self.BIG_SIZE = self.GS + '!\x11'          # Try double both for bigger text
        
        # Alignment
        self.ALIGN_LEFT = self.ESC + 'a\x00'
        self.ALIGN_CENTER = self.ESC + 'a\x01' 
        self.ALIGN_RIGHT = self.ESC + 'a\x02'
        
        # Line spacing
        self.LINE_SPACE_DEFAULT = self.ESC + '2'   # Default line spacing
        self.LINE_SPACE_TIGHT = self.ESC + '0'     # Minimum line spacing
        
        # Emphasis
        self.BOLD_ON = self.ESC + 'E\x01'
        self.BOLD_OFF = self.ESC + 'E\x00'
        self.UNDERLINE_ON = self.ESC + '-\x01'
        self.UNDERLINE_OFF = self.ESC + '-\x00'
        
        # Printer reset commands
        self.PRINTER_RESET = self.ESC + '@'        # Initialize printer
        self.BUFFER_CLEAR = self.ESC + 'c'         # Clear print buffer
    
    def clear_printer_buffer(self):
        """Clear any residual data in printer buffer"""
        try:
            if self.printer_handle:
                # Send reset commands
                self.send_text(self.PRINTER_RESET)
                self.send_text(self.BUFFER_CLEAR)
                print("🗑️ Thermal printer buffer cleared")
                return True
        except Exception as e:
            print(f"⚠️ Could not clear printer buffer: {e}")
        return False
    
    def connect(self, printer_name="XP-80"):
        try:
            self.printer_handle = win32print.OpenPrinter(printer_name)
            print(f"✅ Connected to {printer_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to {printer_name}: {e}")
            return False
    
    def send_text(self, text_cmd):
        """Send text command as individual print job."""
        try:
            job_id = win32print.StartDocPrinter(self.printer_handle, 1, ("Diagonal", None, "RAW"))
            win32print.StartPagePrinter(self.printer_handle)
            win32print.WritePrinter(self.printer_handle, text_cmd.encode('latin-1', errors='replace'))
            win32print.EndPagePrinter(self.printer_handle)
            win32print.EndDocPrinter(self.printer_handle)
        except Exception as e:
            print(f"Print error: {e}")
    
    def set_custom_line_spacing(self, spacing):
        """Set custom line spacing (0-255)."""
        return self.ESC + '3' + chr(spacing)
    
    def print_diagonal_letter(self, letter, style, delay=0.15):
        """Print a single letter diagonally with individual motor burst."""
        
        # Each letter gets its own complete print job - creates motor "tik" sound
        # Subtle style variations - all larger with minor spacing differences
        if style == "COMPACT_TILTED":
            cmd = (self.ROTATE_90_ON + 
                   self.BIG_SIZE +  # Use double both for visible size increase
                   self.set_custom_line_spacing(18) +  # Tighter spacing
                   letter.lower() + "\n" + 
                   self.ROTATE_OFF + 
                   self.NORMAL_SIZE)
        
        elif style == "MEDIUM_TILTED": 
            cmd = (self.ROTATE_90_ON + 
                   self.BIG_SIZE + 
                   self.set_custom_line_spacing(22) +  # Medium spacing
                   letter.lower() + "\n" + 
                   self.ROTATE_OFF + 
                   self.NORMAL_SIZE)
        
        elif style == "RELAXED_TILTED":
            cmd = (self.ROTATE_90_ON + 
                   self.BIG_SIZE + 
                   self.set_custom_line_spacing(26) +  # Slightly wider
                   letter.lower() + "\n" + 
                   self.ROTATE_OFF + 
                   self.NORMAL_SIZE)
        
        elif style == "SPACED_TILTED":
            cmd = (self.ROTATE_90_ON + 
                   self.BIG_SIZE + 
                   self.set_custom_line_spacing(30) +  # More spaced
                   letter.lower() + "\n" + 
                   self.ROTATE_OFF + 
                   self.NORMAL_SIZE)
        
        elif style == "BOLD_TILTED":
            cmd = (self.ROTATE_90_ON + 
                   self.BOLD_ON + 
                   self.BIG_SIZE + 
                   self.set_custom_line_spacing(24) +  # Bold with medium spacing
                   letter.lower() + "\n" + 
                   self.BOLD_OFF + 
                   self.ROTATE_OFF + 
                   self.NORMAL_SIZE)
        
        else:  # "NORMAL_TILTED"
            cmd = (self.ROTATE_90_ON + 
                   self.BIG_SIZE +  # Use bigger size for all
                   self.set_custom_line_spacing(20) +
                   letter.lower() + "\n" + 
                   self.ROTATE_OFF + 
                   self.NORMAL_SIZE)
        
        # CRITICAL: Each letter = separate print job = individual motor burst sound
        self.send_individual_letter(cmd)
        time.sleep(delay)
    
    def send_individual_letter(self, cmd):
        """Send each letter as completely separate print job for motor burst sound."""
        try:
            # Each letter gets its own job - creates distinct "tik" motor sound
            job_id = win32print.StartDocPrinter(self.printer_handle, 1, ("Letter", None, "RAW"))
            win32print.StartPagePrinter(self.printer_handle)
            win32print.WritePrinter(self.printer_handle, cmd.encode('latin-1', errors='replace'))
            win32print.EndPagePrinter(self.printer_handle)
            win32print.EndDocPrinter(self.printer_handle)
            # No delay here - let the rhythm timing handle it
        except Exception as e:
            print(f"Tik error: {e}")
    
    def print_word_diagonally(self, word, style, base_delay=0.0):
        """Print entire word INSTANTLY - all rhythm comes from word pauses."""
        
        # Print ALL letters instantly in rapid succession
        for letter in word.lower():
            # NO delay between letters - true burst within word
            self.print_diagonal_letter(letter, style, 0.0)

        # ALL rhythm and meaning comes from pauses BETWEEN words

        # Minimal spacing between words - fastest possible
        self.send_text("\n")  # Just one line - minimal delay

    def syllable_diagonal_burst(self, text):
        """Print text with syllable-based diagonal styles."""
        
        # Focus on MEANINGFUL RHYTHM instead of pure speed
        word_count = len(re.findall(r'\b\w+\b', text))
        
        # Meaningful rhythm patterns - instant letters, intentional pauses
        style_map = {
            1: ("COMPACT_TILTED", 0.0),     # 1 syllable = instant burst
            2: ("MEDIUM_TILTED", 0.0),      # 2 syllables = instant burst  
            3: ("RELAXED_TILTED", 0.0),     # 3 syllables = instant burst
            4: ("SPACED_TILTED", 0.0),      # 4 syllables = instant burst
            5: ("BOLD_TILTED", 0.0),        # 5+ syllables = instant burst
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            try:
                syllables = syllapy.count(word)
            except:
                syllables = 1
            
            # Get style and timing for this syllable count
            style_info = style_map.get(syllables, ("NORMAL_TILTED", 0.2))
            style, speed = style_info

            self.print_word_diagonally(word, style, speed)            # MEANINGFUL pauses - like real typewriter rhythm patterns
            
            # Create realistic typing patterns based on word complexity
            if syllables == 1:  # Short words = quick transition
                if random.random() < 0.7:  # 70% chance rapid continuation
                    pause = 0.1  # Quick breath
                else:
                    pause = 0.4  # Brief thinking
                    
            elif syllables == 2:  # Medium words = normal rhythm
                if random.random() < 0.5:  # 50/50 chance
                    pause = 0.2  # Normal typing pause
                else:
                    pause = 0.6  # Thinking pause
                    
            elif syllables >= 3:  # Complex words = more thinking
                if random.random() < 0.3:  # 30% chance quick
                    pause = 0.3  # Brief pause
                elif random.random() < 0.7:  # 40% chance thinking  
                    pause = 0.8  # Thinking about next word
                else:
                    pause = 1.2  # Long contemplation
                    
            # Add sentence structure awareness
            if word.endswith(('.', '!', '?')):
                pause += 1.0  # Sentence end = longer pause
            elif word.endswith(','):
                pause += 0.5  # Comma = medium pause

            time.sleep(pause)        # Minimal finishing space 
        self.send_text("\n\n\n")
    
    def diagonal_showcase(self):
        """Showcase all diagonal tilted styles."""
        print("🎨 Diagonal Tilted Showcase - all styles with 'hello':")
        
        styles = [
            ("COMPACT_TILTED", 0.25),
            ("MEDIUM_TILTED", 0.22), 
            ("RELAXED_TILTED", 0.19),
            ("SPACED_TILTED", 0.16),
            ("BOLD_TILTED", 0.13),
            ("NORMAL_TILTED", 0.2)
        ]
        
        for style, speed in styles:
            print(f"\n📐 Testing {style}:")
            self.print_word_diagonally("hello", style, speed)
            time.sleep(1.5)
        
        # Final separator
        self.send_text("\n" + "="*20 + "\nDIAGONAL SHOWCASE COMPLETE\n\n")
    
    def close(self):
        if self.printer_handle:
            win32print.ClosePrinter(self.printer_handle)

def main():
    print("=== Diagonal Tilted Thermal Printer ===")
    print("🔄 Rotated text with variable line spacing!")
    print("📐 COMPACT, MEDIUM, RELAXED, SPACED, BOLD tilted styles")
    print("⚡ INSTANT letter bursts - ALL letters print immediately!")
    print("🎵 MEANINGFUL rhythm - typewriter-style thinking pauses!")
    print("📝 Words burst instantly, pauses show complexity and thought\n")
    
    printer = DiagonalTiltedPrinter()
    
    if not printer.connect():
        return
    
    try:
        while True:
            text = input("Enter text (or 'quit', 'showcase'): ").strip()
            
            if text.lower() in ['quit', 'exit', 'q']:
                break
            elif text.lower() == 'showcase':
                printer.diagonal_showcase()
            elif text:
                printer.syllable_diagonal_burst(text)
                print()
    
    except KeyboardInterrupt:
        pass
    
    printer.close()
    print("\n🎉 Diagonal printing complete!")

if __name__ == "__main__":
    main()