#Prof. Crowes Code in class lmao AAAAAAA

import os
import time
import subprocess

def default_gateway():
    command = "ip route show default | awk '/default/ {print $3}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    gateway_ip = result.stdout.strip()
    return gateway_ip

def ping_command(destination):
    command = ['ping', '-c', '2', destination]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return "FAILED!\n"
    
def main():
    while True:
        print("Please choose an option:")
        print("1. Ping Default Gateway")
        print("2. Test Local Connectivity")
        print("3. Test Remote Connectivity")
        print("4. Test DNS Connectivity")
        print("5. EXIT")

        choice = input("Enter the number of your choice: ")

        if choice == '1':

            os.system('clear')
            print("You selected Option 1.")
            result = default_gateway()
            print("Your Default Gateway: ", result, "\n")

        elif choice == '2':
            os.system('clear')
            print("You selected Option 2.")
            result = default_gateway()
            result = ping_command(result)
            print(result)

        elif choice == '3':
            os.system('clear')
            print("You selected Option 3.")
            result = ping_command("8.8.8.8")
            print(result)

        elif choice == '4':
            os.system('clear')
            print("You selected Option 4.")
            result = ping_command("www.google.com")
            print(result)

        elif choice == '5':
            os.system('clear')
            print("Exiting...")
            time.sleep(2)
            break
        else:
            os.system('clear')
            print("Invalid choice. Please select a number between 1 and 5. \n")
    
if __name__ == "__main__":
    main()

