#How to sign into Open edX by using the edX login and access Office 365 resources


##Create and configure a Microsoft Office 365 account and Azure subscription 

1.  Create an Office 365 account at `https://products.office.com/en-us/business/compare-more-office-365-for-business-plans`

    Login > Configure and Activate your account > Setup Office365 and enable the Single-Sign-On option in Setup 
    
    Note: To run the setup you need at least Internet Explorer 9 (or newer), Windows 7 (or newer), Microsoft .NET Framework 3.5


2.  Create a Microsoft Azure subscription at `http://azure.microsoft.com/en-us/pricing/free-trial/`

    Login > Activate your subscription
     

3.  Create an Azure Active Directory by signing into Microsoft Azure Management Portal at: `https://manage.windowsazure.com/`

    Click on Active Directory > Create a new Active Directory
    
    Choose a name and activate it. The Domain must be the same sa the one that was assigned to your organization, i.e.   
    `http://{organization}.omnicrosoft.com`
    

4.  Create your application
    
    Click on your desired Active Directory > Applications > Add a new appication

    - Specify a “unique” Name for your application (ie. edxsso) (do not use spaces) 
    - Check “Web application and/or web api”
    - APP properties:
        - Sing-on URL :
          * `http://{edx_url}/login`
          * `http://myedxplatform.com/login`
          
        - APP ID URI :
          * `https://{organization}.onmicrosoft.com/{your_app_name}`
          * `https://{organization}.onmicrosoft.com/edxsso`
          
5.  Configure your application

    Click on your desired Active Directory > Applications tab > Select your application (i.e. edxsso) > Configure tab
    
    - Activate Multi-Tenant option
    
    - Create a KEY
    
    - Modify the REPLY URL
      It will be something like this: 
        `http(s)://{your_edx_platform}/auth/complete/azuread-oauth2/`
    
    - Configure Permissions
      Add Windows Azure Active Directory (min perms)
      - Application Permissions: Read directory data 
      - Delegated Permissions:
        - Read and write directory data
        - Enable sign-on and read user's profiles
        
      Add Office 365 SharePoint Online (min perms) 
      - Delegated Permissions:
        - Read items in the site collection 
        - Read users' files
        - [...] Add whatever you need

      Access Rules: OFF
      
        


##Add Azure Active Directory Oauth support to Open edX's third-party authentication module


###Step 1

In  `/edx/app/edxapp/edx-platform/common/djangoapps/third_party_auth/provider.py`:

1.  Import `azuread` from `social.backends`, replacing

  `from social.backends import google, linkedin, facebook`

  with the following:

  `from social.backends import azuread, google, linkedin, facebook`


2.  Add the new class, `AzureADOauth2`, to `provider.py` (see `provider-class.py`).


###Step 2

Copy `azuread.py` to `/edx/app/edxapp/venvs/edxapp/lib/python2.7/site-packages/social/backends/` and reassign the owner as follows:

 `sudo chown edxapp.edxapp /edx/app/edxapp/venvs/edxapp/lib/python2.7/site-packages/social/backends/azuread.py`


###Step 3

Add the AzureAD keys to `/edx/app/edxapp/lms.auth.json` as follows:

```
  "THIRD_PARTY_AUTH": {
        "AzureAD":{
                "SOCIAL_AUTH_AZUREAD_OAUTH2_KEY":"TheKey",
                "SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET":"TheSecret",
                "SOCIAL_AUTH_AZUREAD_OAUTH2_SHAREPOINT_SITE": "TheUrl"
        }
    },
```


In order to enable the Open edX third-party authentication, edit `/edx/app/edxapp/lms.env.json` and set the `ENABLE_THIRD_PARTY_AUTH` variable to `true` as follows:

`"ENABLE_THIRD_PARTY_AUTH": true,`

Additionally, run the `paver` DB command inside the virtual enviroment:

```
sudo -H -u edxapp bash
source /edx/app/edxapp/edxapp_env
cd /edx/app/edxapp/edx-platform
paver update_db --settings=aws


```
##How to customize the sign-in page on the Open edX platform

 
1. The variable `ICON_CLASS = 'fa-windows'` from the class `AzureADOauth2` located at `/edx/app/edxapp/edx-platform/common/djangoapps/third_party_auth/provider.py` defines the Mako variable `${enabled.ICON_CLASS}` used on the CSS to build the button. This CSS class can be modified by rebuilding the SASS files.

2. In order to customize the UI form, edit the mako template: 

    `/edx/app/edxapp/edx-platform/lms/templates/login.html`

