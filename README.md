# 🛡️ GRC Risk Management Project

A pragmatic cyber risk assessment framework for small to medium organizations, featuring automated risk scoring, executive reporting, and interactive dashboards.

## 📋 Project Overview

This repository contains a complete GRC (Governance, Risk, and Compliance) risk management system designed to help organizations identify, assess, and manage their cyber security risks effectively.

**Key Features:**
- ✅ 30 pre-identified common cyber risks
- ✅ Automated risk scoring (inherent & residual)
- ✅ Executive summary with auto-generated KPIs
- ✅ Interactive HTML dashboard with visualizations
- ✅ Asset inventory tracking
- ✅ Risk treatment roadmap

## 🎯 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/SG1unitis/risk-projekt.git
cd risk-projekt
```

### 2. View the Dashboard
Simply open `dashboard.html` in your browser and load `risk_register.csv`

### 3. Run Risk Analysis
```bash
python ./scripts/validate_and_score.py --write --inplace --update-exec
```

This will:
- Validate and calculate all risk scores
- Generate KPIs in `outputs/kpis.json`
- Create top risks report in `outputs/top_risks.md`
- Auto-update `03_executive_summary.md`

## 📁 Project Structure

```
risk-projekt/
├── 01_scope.md                    # Project scope and objectives
├── 02_method.md                   # Risk assessment methodology
├── 03_executive_summary.md        # Executive summary (auto-generated)
├── risk_register.csv              # Master risk register (30 risks)
├── assets_inventory.csv           # Asset inventory
├── roadmap.csv                    # Risk treatment roadmap
├── dashboard.html                 # Interactive risk dashboard
├── scripts/
│   └── validate_and_score.py      # Risk scoring automation
├── outputs/                       # Generated reports
│   ├── kpis.json                  # Key performance indicators
│   └── top_risks.md               # Top risks report
└── .github/                       # GitHub workflows (optional)
```

## 🎨 Dashboard Features

The interactive dashboard (`dashboard.html`) provides:

- **KPI Cards**: Total risks, Critical/High/Medium counts
- **Comparison Charts**: Inherent vs Residual risk levels
- **Risk Reduction Analysis**: Top 10 risks by score reduction
- **5x5 Risk Matrix**: Visual heat map of risks by Likelihood × Impact
- **Top 15 Risks Table**: Detailed view of highest priority risks

![Dashboard Preview](https://via.placeholder.com/800x400/667eea/ffffff?text=Dashboard+Preview)

## 📊 Risk Scoring Methodology

### Inherent Risk
- **Score** = Likelihood (1-5) × Impact (1-5)
- **Levels**: 
  - Critical: 15-25
  - High: 10-14
  - Medium: 5-9
  - Low: 1-4

### Residual Risk (v1.2)
- **Reduce**: L reduced by 1, I reduced by 1 if Resilience/Backups/IR category
- **Accept**: No reduction (residual = inherent)
- **Transfer**: No reduction (residual = inherent)
- **Avoid**: Forced to 1×1 (activity eliminated)

## 🔧 Customization

### Adding New Risks
1. Open `risk_register.csv`
2. Add a new row with risk details
3. Run the validation script
4. Review updated reports

### Modifying Risk Scoring
Edit the `level_from_score()` and residual calculation logic in `validate_and_score.py`

## 📈 Use Cases

This framework is designed for:
- **SMEs** looking to implement basic cyber risk management
- **Security teams** needing to communicate risks to executives
- **Compliance projects** requiring risk documentation (ISO 27001, SOC 2, etc.)
- **Educational purposes** to learn GRC fundamentals

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Risk scenarios based on real-world incidents and industry best practices
- Methodology inspired by ISO 27005 and NIST CSF (pragmatic adaptation for a lightweight risk register)
- Built with pragmatism and business impact in mind

## 📞 Contact

For questions or suggestions, please open an issue or reach out via GitHub.

---

**Made with ❤️ for the security community**

*Last updated: December 2025*
