import os
import time

log_path = os.path.expandvars(r'%LOCALAPPDATA%\FortniteGame\Saved\Logs\FortniteGame.log')
output_file = "raw_dump.txt"

def grab_everything():
    print("Starting log grabber...")
    print(f"📂 Saving to: {output_file}")
    print("---")
    
  
    
    if not os.path.exists(log_path):
        print("ERROR:NO LOG FILE")
        return

    with open(log_path, 'rb') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
        
        f_in.seek(0, 2)
        
        try:
            while True:
                line = f_in.readline()
                if not line:
                    time.sleep(0.01)
                    continue
                
                
                row = line.decode('utf-8', errors='ignore')
                f_out.write(row)
                f_out.flush() # saving
                
                
                if "Log" in row:
                    print(f"DEBUG: {row[:80]}...") 

        except KeyboardInterrupt:
            print(f"\n✅ Finished {output_file}")

if __name__ == "__main__":
    grab_everything()