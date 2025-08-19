# Committed Capital Fee Letter Agent

Professional fee letter generation and email automation system for CC Growth EIS Fund.

## 🎯 Features

- **📊 Excel Integration**: Reads investor, fee, and company data from local Excel files
- **📧 Professional Email**: Sends fee letters via Microsoft Graph API from investors@committedcapital.co.uk
- **🔒 Secure Authentication**: Each employee authenticates with their @committedcapital.co.uk email
- **⚡ Fast Generation**: Create and send fee letters in seconds
- **🎨 Professional Templates**: Beautifully formatted fee letters with company branding
- **📱 User-Friendly Interface**: Simple Streamlit web interface

## 🚀 Quick Start with Pinokio

1. **Install**: Click "Install" to set up the Python environment and dependencies
2. **Start**: Click "Start Fee Letter Agent" to launch the application  
3. **Configure**: Set up your Excel data source on first run
4. **Authenticate**: Sign in with your @committedcapital.co.uk email when prompted
5. **Generate**: Create professional fee letters instantly!

## 📋 Prerequisites

Your IT administrator should have already:
- ✅ Granted you permissions to the `investors@committedcapital.co.uk` shared mailbox
- ✅ Configured Azure App Registration permissions
- ✅ Provided access to the Excel data files

## 🔧 First-Time Setup

### Excel Data Source
On first run, you'll be prompted to select your Excel file containing:
- **InvestorSheet**: Investor information and contact details
- **FeeSheet**: Fee rates and subscription data  
- **CompanySheet**: Company information and share prices

### Authentication
The first time you use email features, you'll authenticate via Microsoft device code flow:
1. A code will appear in the application
2. Go to https://microsoft.com/devicelogin
3. Enter the code and sign in with your **@committedcapital.co.uk** email
4. Grant permissions when prompted
5. Authentication will persist for future sessions

## 💡 Usage Tips

- **Investor Names**: Use full names or be specific (e.g., "James Beckett" not just "James")
- **Company Names**: Must match exactly as they appear in your Excel CompanySheet
- **Draft Mode**: Default mode creates drafts for review before sending
- **Send Mode**: Available for direct email sending after testing

## 🛠️ Troubleshooting

### Email Issues
- Ensure you're authenticated with your **@committedcapital.co.uk** email (not personal)
- Check that you have permissions to the shared mailbox
- Try the "Email Healthcheck" in Settings

### Data Issues  
- Verify your Excel file contains all required sheets
- Check that investor and company names match your Excel data
- Ensure the Excel file is not a cloud placeholder file

### Performance
- Keep Excel files local (not on cloud storage during use)
- Close other applications if fee letter generation seems slow

## 📞 Support

If you encounter issues:
1. Check the application logs in the Pinokio console
2. Try the built-in diagnostics in Settings → Email Healthcheck  
3. Contact your IT administrator for permission-related issues

## 🔒 Security

- All authentication tokens are stored locally and securely
- No sensitive data is transmitted outside your organization
- Each employee authenticates individually for audit trail
- Excel data remains on your local machine

---

**Built for Committed Capital Growth EIS Fund** | Professional fee letter automation made simple
