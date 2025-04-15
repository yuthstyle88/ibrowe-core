import os
import sys
from pathlib import Path
import re
import cairo
import math
import traceback
import subprocess
import shutil

def parse_float(value):
    """Parse a float value, handling 'f' suffix."""
    if not value:
        return None
    return float(value.rstrip('f'))

def parse_icon_file(icon_file):
    """Parse a Brave .icon or .ic file and return the path commands and colors."""
    with open(icon_file, 'r') as f:
        content = f.read().strip()
    
    # Extract canvas dimensions
    canvas_match = re.search(r'CANVAS_DIMENSIONS,\s*(\d+)', content)
    canvas_size = int(canvas_match.group(1)) if canvas_match else 24
    
    # Extract commands and colors
    paths = []
    current_path = {'color': None, 'commands': []}
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('//'):
            continue
            
        parts = [p.strip() for p in line.split(',')]
        command = parts[0]
        
        if command == 'PATH_COLOR_ARGB':
            # If we have a previous path, save it
            if current_path['commands']:
                paths.append(current_path)
            # Start a new path with the color
            current_path = {
                'color': {
                    'a': int(parts[1], 16) / 255.0,
                    'r': int(parts[2], 16) / 255.0,
                    'g': int(parts[3], 16) / 255.0,
                    'b': int(parts[4], 16) / 255.0
                },
                'commands': []
            }
        elif command in ['MOVE_TO', 'LINE_TO', 'CUBIC_TO', 'CLOSE', 'NEW_PATH', 'R_LINE_TO', 'H_LINE_TO', 'V_LINE_TO']:
            # Convert coordinates to floats, handling 'f' suffix
            coords = [parse_float(p) for p in parts[1:]]
            # Filter out None values
            coords = [c for c in coords if c is not None]
            if coords or command in ['CLOSE', 'NEW_PATH']:
                current_path['commands'].append((command, coords))
    
    # Add the last path if it has commands
    if current_path['commands']:
        paths.append(current_path)
    
    return canvas_size, paths

def draw_icon_to_png(commands, output_file, size=128):
    """Draw the icon commands to a PNG file."""
    # Create a new surface and context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surface)
    
    # Clear the background
    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.set_operator(cairo.OPERATOR_SOURCE)
    ctx.paint()
    
    # Scale the context to fit our size
    scale = size / 24  # Default to 24x24 if no size specified
    ctx.scale(scale, scale)
    
    # Enable antialiasing for better quality
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    
    # Current position for relative commands
    current_x = 0
    current_y = 0
    
    # Draw each path
    for path in commands:
        color = path['color']
        if color:
            ctx.set_source_rgba(color['r'], color['g'], color['b'], color['a'])
        
        for cmd, coords in path['commands']:
            try:
                if cmd == 'MOVE_TO':
                    current_x, current_y = coords[0], coords[1]
                    ctx.move_to(current_x, current_y)
                elif cmd == 'LINE_TO':
                    current_x, current_y = coords[0], coords[1]
                    ctx.line_to(current_x, current_y)
                elif cmd == 'R_LINE_TO':
                    current_x += coords[0]
                    current_y += coords[1]
                    ctx.line_to(current_x, current_y)
                elif cmd == 'H_LINE_TO':
                    current_x = coords[0]
                    ctx.line_to(current_x, current_y)
                elif cmd == 'V_LINE_TO':
                    current_y = coords[0]
                    ctx.line_to(current_x, current_y)
                elif cmd == 'CUBIC_TO':
                    ctx.curve_to(coords[0], coords[1], coords[2], coords[3], coords[4], coords[5])
                    current_x, current_y = coords[4], coords[5]
                elif cmd == 'CLOSE':
                    ctx.close_path()
                    ctx.fill()
                elif cmd == 'NEW_PATH':
                    ctx.new_path()
            except Exception as e:
                print(f"Error processing command {cmd} with coords {coords}: {e}")
                continue
    
    # Save to PNG
    surface.write_to_png(output_file)

def convert_icon_to_png(icon_path, output_dir, source_dir):
    try:
        # Get the relative path from the source directory
        relative_path = icon_path.relative_to(source_dir)
        
        # Create a path-based filename by replacing directory separators with underscores
        path_based_name = str(relative_path).replace('/', '__').replace('\\', '__')
        path_based_name = path_based_name.replace('@', 'at')
        path_based_name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in path_based_name)
        
        # Create the output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert the icon to PNG using the path-based name
        output_file = output_dir / f"{path_based_name.replace('.icon', '')}.png"
        
        # Parse the icon file and draw it to PNG
        canvas_size, paths = parse_icon_file(icon_path)
        draw_icon_to_png(paths, str(output_file), size=canvas_size)
        
        print(f"Successfully converted {icon_path} to {output_file}")
        return True
    except Exception as e:
        print(f"Error converting {icon_path}: {str(e)}")
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_icons.py <source_dir> <output_dir>")
        sys.exit(1)
        
    source_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    if not source_dir.exists():
        print(f"Source directory {source_dir} does not exist")
        sys.exit(1)
        
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all .icon files recursively
    icon_files = list(source_dir.rglob("*.icon"))
    
    if not icon_files:
        print(f"No icon files found in {source_dir}")
        sys.exit(1)
        
    print(f"Found {len(icon_files)} icon files")
    
    # Convert each icon file
    success_count = 0
    for icon_file in icon_files:
        if convert_icon_to_png(icon_file, output_dir, source_dir):
            success_count += 1
            
    print(f"\nSuccessfully converted {success_count} files to PNG format")
    print(f"Output directory: {output_dir}")
    
    # Print files in the output directory
    print("\nConverted files:")
    for file in sorted(output_dir.glob('*.png')):
        print(f"    {file.name}")

if __name__ == "__main__":
    main() 