# Committed Capital Fee Generator - Comprehensive User Guide

## Table of Contents
1. [Initial Setup](#initial-setup)
2. [Excel File Requirements](#excel-file-requirements)
3. [First Launch & Configuration](#first-launch--configuration)
4. [Using the Fee Generator](#using-the-fee-generator)
5. [Understanding the Results](#understanding-the-results)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## Initial Setup

### Prerequisites
- Python 3.8 or higher installed on your system
- Access to the Committed Capital Fee Generator application
- Microsoft Excel or compatible spreadsheet software

### Installation
1. Download the application files to your local machine
2. Open a terminal/command prompt in the application directory
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch the application:
   ```bash
   streamlit run vc_agent_streamlit.py
   ```

---

## Excel File Requirements

### File Structure
Your Excel file must contain **three separate sheets** with specific column names:

#### 1. InvestorSheet
**Required Columns:**
- `First Name` - Investor's first name
- `Last Name` - Investor's last name  
- `Contact email` - Investor's email address
- `Salutation` - How to address the investor (e.g., "Dear")
- `Custodian Client Ref` - Unique reference number
- `Investor Type` - Classification (Professional/Retail)

**Example Data:**
| First Name | Last Name | Contact email | Salutation | Custodian Client Ref | Investor Type |
|------------|-----------|---------------|------------|---------------------|---------------|
| John | Smith | john.smith@email.com | Dear | CC001 | Professional |
| Jane | Doe | jane.doe@email.com | Dear | CS002 | Retail |

#### 2. CompanySheet
**Required Columns:**
- `Company Name` - Full company name
- `Current Share Price` - Share price in GBP (e.g., 0.05)
- `Share Class` - Type of shares (e.g., "Ordinary Share")
- `Fund Type` - Investment type (e.g., "EIS", "KIC")

**Example Data:**
| Company Name | Current Share Price | Share Class | Fund Type |
|--------------|-------------------|-------------|-----------|
| Ceed Ltd | 0.05 | Ordinary Share | EIS |
| TechCorp Ltd | 0.10 | A Ordinary Share | KIC |

#### 3. FeeSheet
**Required Columns:**
- `Custodian Client Ref` - Must match InvestorSheet
- `Fund` - Fund name/identifier
- `CC Set up fee %` - Upfront fee percentage (e.g., 2.0)
- `CC AMC %` - Annual Management Charge percentage (e.g., 2.0)
- `CC Carry %` - Performance fee percentage (e.g., 20.0)
- `Gross/Net` - Investment type ("Gross" or "Net")
- `Subscription code` - Optional reference code

**Example Data:**
| Custodian Client Ref | Fund | CC Set up fee % | CC AMC % | CC Carry % | Gross/Net | Subscription code |
|---------------------|------|------------------|-----------|------------|-----------|-------------------|
| CC001 | EIS Fund 1 | 2.0 | 2.0 | 20.0 | Gross | CC-EIS-001 |
| CS002 | EIS Fund 1 | 2.0 | 2.0 | 20.0 | Net | CS-EIS-002 |

### Important Notes
- **Column names must match exactly** (case-sensitive)
- **Custodian Client Ref** links InvestorSheet to FeeSheet
- **Share prices** should be in GBP (e.g., 0.05 not £0.05)
- **Percentages** can be entered as decimals (0.02) or whole numbers (2.0)
- **Investment Type** determines fee calculation method

---

## First Launch & Configuration

### 1. Launch the Application
- Run `streamlit run vc_agent_streamlit.py`
- Your default web browser will open automatically
- The application will load with a welcome screen

### 2. Configure Excel File Path
1. Click on **Settings** in the sidebar
2. In the **Excel Configuration** section:
   - Click **Browse** to select your Excel file
   - Or manually enter the full file path
   - Click **Save Configuration**
3. Verify the path is saved correctly

### 3. Test Excel Connection
1. Go to **Excel Data** in the sidebar
2. Click **Test Excel Connection**
3. You should see:
   - ✅ Excel file found and accessible
   - ✅ All three sheets detected
   - ✅ Column structure validated

### 4. Verify Data Loading
1. Click **View Investors** to see loaded investor data
2. Click **View Companies** to see loaded company data
3. Ensure all required fields are populated

---

## Using the Fee Generator

### 1. Access the Fee Generator
- Click **Fee Letter Generator** in the sidebar
- You'll see the main fee generation form

### 2. Fill in Basic Information
**Required Fields:**
- **Investor Name**: Type the investor's full name (e.g., "John Smith")
- **Investment Amount**: Enter the amount in GBP (e.g., 50000.50)
- **Company Name**: Type the company name (e.g., "Ceed Ltd")

**How to Enter:**
- **Investor Name**: Use first and last name as it appears in Excel
- **Investment Amount**: Include decimals if needed (e.g., 50000.50)
- **Company Name**: Use exact company name from Excel

### 3. Optional Overrides
Click **⚙️ Override variables (optional)** to customize:

**Fee Percentages:**
- **Upfront Fee %**: Override setup fee percentage
- **AMC 1-3 %**: Override first 3 years management charge
- **AMC 4-5 %**: Override years 4-5 management charge
- **Carry %**: Override performance fee percentage

**Other Settings:**
- **Share Price Override**: Custom share price for this transaction
- **Investment Type**: Force Gross or Net calculation
- **Investor Type**: Override Professional/Retail classification
- **Share Class**: Custom share class
- **Number of Shares**: Override calculated share quantity

### 4. Generate Fee Letter
1. Click **Generate Fee Letter** button
2. Wait for processing (you'll see a spinner)
3. Review the generated results

---

## Understanding the Results

### 1. Fee Letter Summary
The top section shows:
- **Investor**: Name and classification
- **Investment**: Amount and type (Gross/Net)
- **Company**: Target company
- **Fees**: Breakdown of all charges
- **Status**: Ready to send or needs review

### 2. Fee Letter Preview
**Main Details:**
- **Investor Information**: Name, type, email
- **Investment Details**: Amount, type, company
- **Fee Breakdown**: All charges with VAT included
- **Share Information**: Quantity, price, class
- **Total Transfer**: Amount including all fees

**Share Quantity Note:**
- Appears when shares have decimals
- Shows recommended rounded quantity
- Includes investment amount for rounded shares

### 3. Fee Calculations
**Gross Investment:**
- Original amount entered
- Fees are additional to this amount
- Total transfer = Gross + Fees

**Net Investment:**
- Amount after fees are deducted
- Fees are subtracted from total
- Total transfer = Net + Fees

**VAT Handling:**
- All fees include VAT automatically
- UK VAT rates are applied
- No VAT override needed

### 4. Email Functionality
- **Recipient Email**: Automatically populated from Excel
- **Preview Mode**: Review before sending
- **Send Mode**: Actually send the email
- **Team Review**: Send to team before investor

---

## Troubleshooting

### Common Issues

#### 1. Excel File Not Found
**Symptoms:** "Excel file not found" error
**Solutions:**
- Check file path in Settings
- Ensure file exists and is accessible
- Verify file permissions
- Try absolute path instead of relative

#### 2. Missing Data Errors
**Symptoms:** "Missing required fields" message
**Solutions:**
- Check Excel column names match exactly
- Ensure all required columns have data
- Verify Custodian Client Ref links correctly
- Check for empty cells in required fields

#### 3. Fee Calculation Errors
**Symptoms:** Incorrect fee amounts or errors
**Solutions:**
- Verify percentage values in FeeSheet
- Check Gross/Net classification
- Ensure share prices are numeric
- Review fee override values

#### 4. Investor/Company Not Found
**Symptoms:** "Investor not found" or "Company not found"
**Solutions:**
- Check spelling in form fields
- Verify names match Excel exactly
- Ensure data is loaded (check Excel Data section)
- Refresh Excel cache if needed

### Error Messages Explained

| Error Message | What It Means | How to Fix |
|---------------|----------------|------------|
| "Excel adapter failed" | Can't read Excel file | Check file path and permissions |
| "Investor not found" | Name doesn't match Excel | Use exact name from InvestorSheet |
| "Company not found" | Company name mismatch | Use exact name from CompanySheet |
| "Missing fee data" | No FeeSheet entry | Check Custodian Client Ref link |
| "Invalid amount" | Amount format error | Use numeric values only |

---

## Best Practices

### 1. Excel File Management
- **Keep one master file** with all data
- **Backup regularly** before making changes
- **Use consistent naming** for companies and funds
- **Validate data** before using in production

### 2. Data Entry
- **Double-check percentages** (2.0 vs 0.02)
- **Use consistent formats** for share prices
- **Verify Custodian Client Ref** links
- **Test with small amounts** first

### 3. Fee Generation
- **Review all overrides** before generating
- **Check share quantities** for decimals
- **Verify fee calculations** match expectations
- **Use preview mode** before sending

### 4. Email Management
- **Always preview** before sending
- **Use team review** for important letters
- **Keep records** of sent letters
- **Verify recipient emails** are correct

---

## Advanced Features

### 1. Bulk Operations
- Generate multiple fee letters
- Use consistent overrides
- Batch email sending
- Export results

### 2. Custom Templates
- Modify fee letter content
- Add company branding
- Customize fee descriptions
- Include additional terms

### 3. Audit Trail
- Track all generated letters
- Monitor fee calculations
- Export audit reports
- Compliance documentation

---

## Support & Maintenance

### Regular Tasks
- **Weekly**: Verify Excel data integrity
- **Monthly**: Review fee calculations
- **Quarterly**: Update fee percentages
- **Annually**: Archive old data

### Data Validation
- Check for duplicate entries
- Verify percentage accuracy
- Validate email addresses
- Review share price updates

### System Updates
- Keep application updated
- Monitor for new features
- Review security updates
- Backup configuration

---

## Quick Reference

### Essential Commands
```bash
# Launch application
streamlit run vc_agent_streamlit.py

# Install dependencies
pip install -r requirements.txt

# Check Python version
python --version
```

### Key Excel Columns
- **InvestorSheet**: First Name, Last Name, Contact email, Custodian Client Ref
- **CompanySheet**: Company Name, Current Share Price, Share Class
- **FeeSheet**: Custodian Client Ref, CC Set up fee %, CC AMC %, CC Carry %, Gross/Net

### Common Overrides
- **Upfront Fee**: 2.0% (typical)
- **AMC**: 2.0% (years 1-3), 1.5% (years 4-5)
- **Carry**: 20.0% (performance fee)
- **VAT**: Fixed at UK rates (no override needed)

---

This guide covers the complete setup and usage of the Committed Capital Fee Generator. For additional support or questions, refer to the application's built-in help features or contact the development team.
