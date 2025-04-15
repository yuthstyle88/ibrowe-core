#!/bin/bash

# Create output directories
mkdir -p output/svg_files
mkdir -p output/png_icon_files

# Function to convert icon path definition to SVG
convert_to_svg() {
    local input_file="$1"
    local output_file="$2"
    local width=16
    local height=16

    # Create SVG header
    echo '<?xml version="1.0" encoding="UTF-8"?>' > "$output_file"
    echo "<svg width=\"${width}\" height=\"${height}\" viewBox=\"0 0 ${width} ${height}\" xmlns=\"http://www.w3.org/2000/svg\">" >> "$output_file"
    
    # Read the icon file and convert paths to SVG
    local current_color=""
    local path_data=""
    
    while IFS=, read -r cmd values; do
        case $cmd in
            "CANVAS_DIMENSIONS")
                width=$(echo "$values" | cut -d',' -f1)
                height=$width
                ;;
            "PATH_COLOR_ARGB")
                if [ -n "$path_data" ]; then
                    echo "<path d=\"$path_data\" fill=\"$current_color\"/>" >> "$output_file"
                    path_data=""
                fi
                # Convert ARGB values to hex color
                local alpha=$(echo "$values" | cut -d',' -f1 | tr -d ' ')
                local red=$(echo "$values" | cut -d',' -f2 | tr -d ' ')
                local green=$(echo "$values" | cut -d',' -f3 | tr -d ' ')
                local blue=$(echo "$values" | cut -d',' -f4 | tr -d ' ')
                current_color="#${red}${green}${blue}"
                ;;
            "MOVE_TO")
                local x=$(echo "$values" | cut -d',' -f1 | tr -d 'f ')
                local y=$(echo "$values" | cut -d',' -f2 | tr -d 'f ')
                path_data="${path_data}M${x},${y}"
                ;;
            "LINE_TO")
                local x=$(echo "$values" | cut -d',' -f1 | tr -d 'f ')
                local y=$(echo "$values" | cut -d',' -f2 | tr -d 'f ')
                path_data="${path_data}L${x},${y}"
                ;;
            "R_LINE_TO")
                local x=$(echo "$values" | cut -d',' -f1 | tr -d 'f ')
                local y=$(echo "$values" | cut -d',' -f2 | tr -d 'f ')
                path_data="${path_data}l${x},${y}"
                ;;
            "H_LINE_TO")
                local x=$(echo "$values" | cut -d',' -f1 | tr -d 'f ')
                path_data="${path_data}H${x}"
                ;;
            "V_LINE_TO")
                local y=$(echo "$values" | cut -d',' -f1 | tr -d 'f ')
                path_data="${path_data}V${y}"
                ;;
            "CLOSE")
                path_data="${path_data}Z"
                ;;
            "NEW_PATH")
                if [ -n "$path_data" ]; then
                    echo "<path d=\"$path_data\" fill=\"$current_color\"/>" >> "$output_file"
                    path_data=""
                fi
                ;;
        esac
    done < "$input_file"

    # Add any remaining path
    if [ -n "$path_data" ]; then
        echo "<path d=\"$path_data\" fill=\"$current_color\"/>" >> "$output_file"
    fi

    # Close SVG
    echo "</svg>" >> "$output_file"
}

# Function to convert SVG to PNG
convert_svg_to_png() {
    local input_file="$1"
    local output_file="$2"
    
    # Convert SVG to PNG using ImageMagick
    magick convert "$input_file" "$output_file"
}

# Process each icon file
find output/icon_files -type f -name "*.icon" | while read -r file; do
    # Get the base name without extension
    base_name=$(basename "$file" .icon)
    
    # Convert to SVG first
    svg_file="output/svg_files/${base_name}.svg"
    convert_to_svg "$file" "$svg_file"
    
    # Then convert SVG to PNG
    png_file="output/png_icon_files/${base_name}.png"
    convert_svg_to_png "$svg_file" "$png_file"
done

echo "Conversion complete. PNG files are in output/png_icon_files" 