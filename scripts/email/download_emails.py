import sys, os, re, json
import imaplib
import getpass
import pandas as pd

PROJ_ROOT = os.environ['PROJ_ROOT']
with open(PROJ_ROOT + 'parameters.json') as parameter_json:
    params = json.load(parameter_json)

imap_params = params['IMAP']

IMAP_SERVER = imap_params['IMAP_SERVER']
EMAIL_FOLDERS = imap_params['EMAIL_FOLDERS']
EMAIL_DOMAIN = imap_params['EMAIL_DOMAIN']
PASSWORD = imap_params['PASSWORD']
print(EMAIL_FOLDERS)

EMAIL_DIR = imap_params['EMAIL_DIR']
print(EMAIL_DIR)

ACCOUNT_LIST = imap_params['ACCOUNT_LIST']
print(ACCOUNT_LIST)

re_gthread = re.compile('X-GM-THRID (\d*)')
re_gmMsgid = re.compile('X-GM-MSGID (\d*)')

def extract_regex(string_to_search, compiled_regex):
    match = compiled_regex.search(string_to_search)
    if match:
        return match.group(1)
    else:
        return ''

def download_folder(M, account_prefix, folder):
    """
    Download full content email and retrieve GMail IMAP extension identifiers.
    Return a json containing ['email','X-GM-MSGID','X-GM-THRID']
        X-GM-MSGID: Unique and immutable identifier for every email in GMail
        X-GM-THRID: Thread ID for GMail
        email:      String handle for e-mail on disk '<folder>/<account>.<num>.eml'
        <num>:      Sequence number retrieved by IMAP.fetch()
    """
    
    # Obtain sequence numbers of all emails contained in this mailbox folder
    rv, seq_nums = M.search(None, "ALL")
    #  e.g. ['1 2 3 4 5']
    
    if rv != 'OK':
        print ("No messages found!")
        return
    
    # List of dictionaries
    email_ids = []
    
    email_prefix = folder + '/' + account_prefix + '.'
    email_postfix = '.eml'

    for num in seq_nums[0].split():
        email_id = {}

        rv, email_identifiers = M.fetch(num, "(X-GM-MSGID X-GM-THRID)")
        
        if rv != 'OK':
            print ("ERROR getting message", num)
            return
        else:
            # M.fetch() returns unparsed tuple of strings. Parse after download
            email_id['email'] = email_prefix + num + email_postfix
            gthread_gmsgid_string = email_identifiers[0]
            email_id['X-GM-THRID'] = extract_regex(gthread_gmsgid_string, re_gthread)
            email_id['X-GM-MSGID'] = extract_regex(gthread_gmsgid_string, re_gmMsgid)

            email_ids.append(email_id)
            print("Processed email: " + str(num))
            
            # Download the entire e-mail and write to disk
            rv, data = M.fetch(num, '(RFC822)')
            if rv != 'OK':
                print ("ERROR getting message", num)
                return
            else:
                print ("Writing message " + email_id['email'])
                f = open('%s/%s.eml' %(os.getcwd(), account_prefix+'.'+num), 'wb')
                f.write(data[0][1])
                f.close()

    return email_ids

def main():
    if not os.path.exists(EMAIL_DIR):
        os.makedirs(EMAIL_DIR)
    for folder in EMAIL_FOLDERS:
        if folder in os.listdir(EMAIL_DIR):
            print("Found "+folder+" in data directory")
        else:
            print("Making folder " + folder)
            os.mkdir(EMAIL_DIR+folder)

    os.chdir(EMAIL_DIR)
    print(os.getcwd())

    email_id_list = []
    
    for account in ACCOUNT_LIST:
        print(account)
        email_account = account + EMAIL_DOMAIN
        try:  
            M = imaplib.IMAP4_SSL(IMAP_SERVER)
            M.login(email_account, PASSWORD)

            for folder in EMAIL_FOLDERS:
                os.chdir(EMAIL_DIR+folder)
                print(os.getcwd())
                print("Processing mailbox: ", folder)
                rv, data = M.select(folder)

                if rv == 'OK':
                    email_id_list.extend(download_folder(M,account,folder))
                    M.close()
                else:
                    print ("ERROR: Unable to open mailbox ", rv)

            M.logout()
        except Exception:
            raise

    df_email_id = pd.DataFrame(email_id_list)
    
    out_columns = [u'email', u'X-GM-MSGID', u'X-GM-THRID']#, u'message_id']
    df_email_id[out_columns].to_csv(EMAIL_DIR + "email_ids.csv", index=False)

    print("Wrote email ids to " + EMAIL_DIR + "email_ids.csv")
    
if __name__ == "__main__":
    main()
