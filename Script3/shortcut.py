#Emir T. Yilmaz
#October 10th, 2025
#Script 3

import os # For os.symlink(), os.unlink(), os.path, os.walk()
import sys # For sys.exit()
import pathlib # For pathlib.Path

#Used copoilet to add comments! bcz yes i like having all these comments made to read lowk.

home = pathlib.Path.home() # User's home directory
desktop = home / "Desktop" # Path to Desktop
os.system("clear") # Clear the terminal screen
print("Current Working Directory:", os.getcwd()) # Print current working directory

while True: # Main loop
    print("\n===============================")
    print("     SYMBOLIC LINK MANAGER     ")
    print("===============================")
    print("[1] Create a symbolic link")
    print("[2] Delete a symbolic link")
    print("[3] Generate a symbolic link report")
    print("[4] Quit")

    choice = input("Select an option (1-4) or type 'quit': ").strip().lower() # Get user choice

    if choice in ("4", "quit"): # Exit option
        print("Goodbye!") # Exit message
        sys.exit(0) # Exit the program

    elif choice == "1": # Create symbolic link
        print("\n=== Create Symbolic Link ===") # Section header
        filename = input("Enter the name of the file to create a symbolic link for: ").strip() # Get filename
        if not filename: # Check for empty input
            print("Error: File name cannot be empty.") 
            continue
        matches = [] # List to store matching file paths
        for root, dirs, files in os.walk(home): # Walk through home directory
            for f in files: # Check each file
                if f == filename: # If filename matches
                    matches.append(os.path.join(root, f)) # Add full path to matches
        if not matches: # No matches found
            print(f"Error: No file named '{filename}' found in your home directory.") 
            continue
        if len(matches) > 1: # Multiple matches found
            print(f"\nMultiple files with the name '{filename}' were found:") # List matches
            for i, path in enumerate(matches, 1): # Enumerate matches
                print(f"[{i}] {path}") # Print each match
            while True:
                try:
                    selection = int(input(f"Select the file to create a shortcut for (1-{len(matches)}): ")) # Get user selection
                    if 1 <= selection <= len(matches): # Validate selection
                        target = matches[selection - 1] # Get selected target
                        break
                    else:
                        print("Error: Invalid selection. Try again.") # Handle out-of-range input
                except ValueError:
                    print("Error: Enter a valid number.") # Handle non-integer input
        else:
            target = matches[0] # Single match found
        link_path = desktop / filename # Path for the symbolic link on Desktop
        if link_path.exists(): # Check if link already exists
            print("Error: A link or file with that name already exists on your Desktop.") 
            continue
        try:
            os.symlink(target, link_path) # Create the symbolic link
            print("Shortcut created on Desktop →", link_path) # Success message
        except OSError as e: # Handle errors during link creation
            print("Error creating symbolic link:", e) # Print error message

    elif choice == "2": # Delete symbolic link
        print("\n=== Delete Symbolic Link ===") # Section header
        link_name = input("Enter the name of the symbolic link to delete: ").strip() # Get link name
        link_path = desktop / link_name # Path to the symbolic link on Desktop
        if not link_path.exists(): # Check if link exists
            print("Error: That symbolic link does not exist on your Desktop.") 
            continue
        if not link_path.is_symlink(): # Check if it's a symbolic link
            print("Error: That file exists but is not a symbolic link.") 
            continue
        try:
            link_path.unlink() # Delete the symbolic link
            print("Deleted symbolic link:", link_path) # Success message
        except OSError as e: # Handle errors during deletion
            print("Error deleting symbolic link:", e) # Print error message

    elif choice == "3": # Generate symbolic link report
        print("\n=== Symbolic Link Report ===") # Section header
        symlinks = [] # List to store found symbolic links
        for root, dirs, files in os.walk(home): # Walk through home directory
            for f in files: # Check each file
                full_path = os.path.join(root, f) # Get full file path
                if os.path.islink(full_path): # Check if it's a symbolic link
                    target = os.readlink(full_path) # Get the target of the symbolic link
                    symlinks.append((full_path, target)) # Add to list
        if not symlinks: # No symbolic links found
            print("No symbolic links found in your home directory.") # Print message
            report_lines = ["No symbolic links found in your home directory."] # Build report content for file
        else:
            print("\nFound symbolic links:") #  Section header
            print("-" * 60) # Separator line
            report_lines = ["Found symbolic links:\n" + "-" * 60] # Start report content
            for link, target in symlinks: # Print each symbolic link and its target
                block = f"Link: {link}\n→ Target: {target}\n" # Prepare line block
                print(block, end="") # Print link and target
                report_lines.append(block.rstrip("\n")) # Append to report content
            print("-" * 60) # Separator line
            print(f"Total symbolic links in home directory: {len(symlinks)}") # Print total count
            report_lines.append("-" * 60) # Add separator to report content
            report_lines.append(f"Total symbolic links in home directory: {len(symlinks)}") # Add total count

        out_path = home / "symlink_report.txt" # Save report in HOME directory (not Desktop)
        try:
            with open(out_path, "w", encoding="utf-8") as f: # Open report file for writing
                f.write("\n".join(report_lines) + "\n") # Write report content to file
            print(f"\nReport saved to: {out_path}") # Inform user where it was saved
        except OSError as e:
            print("Error writing report file:", e) # Print error if save fails

    else:
        print("Invalid selection. Please try again.") # Handle invalid input