master_reset_list = {}

def master_reset_add(email, generated_otp):  # Adding akey value pair to master object
    
    master_reset_list[email] = generated_otp
    
    return 
    
    
def master_reset_fetch(email):  # Fetching element from master object
    
    fetch_otp = master_reset_list[email]
    
    return fetch_otp
    
def master_reset_delete(email):  # Deleteing an element from master object
    
    master_reset_list.pop(email)
    
    return 