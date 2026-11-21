# Sample (illustrative) data for SAMA CSF maturity self-assessment portfolio tool.
# Structure (domains/subdomains/maturity levels) from SAMA CSF v1.0 (SAMA Rulebook).
# Levels, owners, evidence, actions are SAMPLE data. Framework mappings are indicative.
D = {"3.1":"Cyber Security Leadership and Governance","3.2":"Cyber Security Risk Management and Compliance",
     "3.3":"Cyber Security Operations and Technology","3.4":"Third Party Cyber Security"}
DA = {"3.1":"القيادة والحوكمة","3.2":"إدارة المخاطر والامتثال","3.3":"العمليات والتقنية","3.4":"الأطراف الثالثة"}
# id, name, arabic, level, owner, evidence, action, due, NIST CSF 2.0, ISO 27001:2022 Annex A, PCI DSS v4.0
ROWS = [
("3.1.1","Cyber Security Governance","حوكمة الأمن السيبراني",3,"CISO","Approved committee charter; quarterly minutes","Add KPIs to committee reporting","2027-03-31","GV.RR, GV.OV","5.2, 5.4","12.4"),
("3.1.2","Cyber Security Strategy","استراتيجية الأمن السيبراني",2,"CISO","Draft strategy, not board-approved","Approve strategy and align with business objectives","2027-02-28","GV.OC","5.1","—"),
("3.1.3","Cyber Security Policy","سياسة الأمن السيبراني",3,"GRC","Approved policy; annual review record","Track policy compliance in GRC tool","2027-04-30","GV.PO","5.1","12.1"),
("3.1.4","Cyber Security Roles and Responsibilities","الأدوار والمسؤوليات",3,"HR","RACI matrix approved","Link roles to job descriptions","2027-03-31","GV.RR","5.2","12.4"),
("3.1.5","Cyber Security in Project Management","الأمن السيبراني في إدارة المشاريع",2,"PMO","Security checklist used informally","Formalize security gate in project lifecycle","2027-05-31","GV.OC, PR.PS","5.8","6.2"),
("3.1.6","Cyber Security Awareness","التوعية بالأمن السيبراني",3,"GRC","Approved yearly awareness plan; campaign records","Measure effectiveness with phishing simulations","2027-01-31","PR.AT","6.3","12.6"),
("3.1.7","Cyber Security Training","التدريب على الأمن السيبراني",2,"HR","Ad-hoc training sessions","Define role-based training plan","2027-04-30","PR.AT","6.3","12.6"),
("3.2.1","Cyber Security Risk Management","إدارة مخاطر الأمن السيبراني",3,"GRC","Central risk register; treatment plans","Introduce KRIs and trend reporting","2027-03-31","GV.RM, ID.RA","5.7, Clause 6.1","12.3"),
("3.2.2","Regulatory Compliance","الامتثال التنظيمي",3,"Compliance","Regulatory requirements register","Automate compliance monitoring","2027-06-30","GV.OC","5.31","—"),
("3.2.3","Compliance with (Inter)national Industry Standards","الامتثال للمعايير المحلية والدولية",2,"Compliance","PCI DSS scope defined; SWIFT CSP self-attestation","Formal gap assessment against PCI DSS v4.0","2027-05-31","GV.OC","5.31, 5.36","All"),
("3.2.4","Cyber Security Review","مراجعة الأمن السيبراني",2,"GRC","Annual review, not structured","Define review methodology and schedule","2027-04-30","ID.IM","5.35","11.3"),
("3.2.5","Cyber Security Audits","تدقيق الأمن السيبراني",3,"Internal Audit","Approved audit plan; last audit report","Track audit findings to closure","2027-02-28","ID.IM","5.35","12.4"),
("3.3.1","Human Resources","الموارد البشرية",3,"HR","Screening records; signed NDAs","Add security clauses to exit process","2027-03-31","GV.RR, PR.AA","6.1, 6.2, 6.5","12.7"),
("3.3.2","Physical Security","الأمن المادي",3,"Facilities","Access card logs; CCTV","Periodic review of data center access","2027-02-28","PR.AA","7.1, 7.2","9"),
("3.3.3","Asset Management","إدارة الأصول",2,"IT Operations","Asset inventory template; partial server data","Complete inventory and classification for all assets","2027-01-31","ID.AM","5.9, 5.12","12.5"),
("3.3.4","Cyber Security Architecture","البنية الأمنية",2,"Security Architecture","Network diagrams, not approved","Define and approve security architecture standard","2027-06-30","PR.IR","8.27","1"),
("3.3.5","Identity and Access Management","إدارة الهويات والصلاحيات",3,"IT Operations","Approved IAM procedure; quarterly access reviews","Measure on-time review rate (KCI)","2027-03-31","PR.AA","5.15, 5.18, 8.2","7, 8"),
("3.3.6","Application Security","أمن التطبيقات",2,"App Development","Code reviews done informally","Adopt secure SDLC and SAST","2027-06-30","PR.PS","8.25, 8.26, 8.28","6"),
("3.3.7","Change Management","إدارة التغيير",3,"IT Operations","Approved change process; CAB records","Add security impact assessment to changes","2027-04-30","PR.PS","8.32","6.5"),
("3.3.8","Infrastructure Security","أمن البنية التحتية",3,"IT Operations","Hardening baselines; firewall reviews","Monitor baseline compliance automatically","2027-05-31","PR.PS, PR.IR","8.9, 8.20, 8.22","1, 2"),
("3.3.9","Cryptography","التشفير",2,"Security Architecture","Encryption used, no approved standard","Approve cryptography standard and key management","2027-05-31","PR.DS","8.24","3, 4"),
("3.3.10","Bring Your Own Device (BYOD)","الأجهزة الشخصية",1,"IT Operations","No formal BYOD controls","Define BYOD policy and MDM","2027-02-28","PR.AA, PR.PS","8.1, 6.7","—"),
("3.3.11","Secure Disposal of Information Assets","الإتلاف الآمن للأصول",2,"IT Operations","Disposal done, no certificates kept","Formalize disposal procedure with records","2027-03-31","PR.DS","7.14, 8.10","9.4"),
("3.3.12","Payment Systems","أنظمة الدفع",3,"Payments","Payment systems hardening; PCI scope","Continuous PCI control monitoring","2027-04-30","PR.DS, PR.PS","8.20, 8.24","1–12"),
("3.3.13","Electronic Banking Services","الخدمات المصرفية الإلكترونية",3,"Digital Channels","MFA for customers; fraud monitoring","Measure fraud KRIs","2027-05-31","PR.AA, DE.CM","8.5","8"),
("3.3.14","Cyber Security Event Management","إدارة الأحداث الأمنية",3,"SOC","SIEM use cases; log retention","Tune use cases with detection metrics","2027-03-31","DE.CM, DE.AE","8.15, 8.16","10"),
("3.3.15","Cyber Security Incident Management","إدارة الحوادث الأمنية",3,"SOC","Approved IR plan; incident records","Run annual IR tabletop exercise","2027-02-28","RS.MA, RS.AN, RC.RP","5.24, 5.25, 5.26","12.10"),
("3.3.16","Threat Management","إدارة التهديدات",2,"SOC","Threat feeds received, not analyzed","Formal threat intelligence process","2027-06-30","ID.RA, DE.AE","5.7","—"),
("3.3.17","Vulnerability Management","إدارة الثغرات",3,"IT Operations","Monthly scans; patch SLA","Track overdue critical vulnerabilities (KRI)","2027-01-31","ID.RA, PR.PS","8.8","6.3, 11.3"),
("3.4.1","Contract and Vendor Management","العقود وإدارة الموردين",2,"Procurement","Security clauses in some contracts","Standard security clauses and vendor risk assessment","2027-03-31","GV.SC","5.19, 5.20","12.8"),
("3.4.2","Outsourcing","التعهيد",2,"Procurement","Outsourcing list, no security review","Security review before outsourcing approval","2027-04-30","GV.SC","5.21, 5.22","12.8"),
("3.4.3","Cloud Computing","الحوسبة السحابية",2,"IT Operations","Cloud usage inventory","Cloud security policy and provider assessment","2027-05-31","GV.SC, PR.PS","5.23","12.8, A1"),
]
LEVELS=[(0,"Non-existent","غير موجود","No documentation and no awareness of the control.","ما فيه توثيق ولا وعي بالضابط."),
(1,"Ad-hoc","عشوائي","Partially defined and performed inconsistently.","معرّف جزئيًا وينطبق بشكل غير منتظم."),
(2,"Repeatable but informal","متكرر غير رسمي","Repeated in a standard way, but not documented or approved.","يتكرر بطريقة ثابتة، بس غير موثق ولا معتمد."),
(3,"Structured and formalized","موثق ومعتمد","Defined, approved and implemented; can be demonstrated with evidence; KPIs monitored.","معرّف ومعتمد ومطبق، ويُثبت بالأدلة، ومراقب بمؤشرات أداء."),
(4,"Managed and measurable","يُدار ويُقاس","Effectiveness periodically measured with KRIs and trend reporting.","فعاليته تُقاس بشكل دوري بمؤشرات المخاطر."),
(5,"Adaptive","متطور","Continuous improvement, integrated with enterprise risk, benchmarked with the sector.","تحسين مستمر، ومدمج مع إدارة المخاطر، ومقارن بالقطاع.")]
# SWIFT CSCF objective numbers (1-7) and Basel Committee Principles for Operational Resilience (2021, P1-P7). Indicative.
EXTRA={
"3.1.1":("—","P1"),"3.1.2":("—","P1"),"3.1.3":("—","P1"),"3.1.4":("—","P1"),"3.1.5":("—","P2"),
"3.1.6":("Obj 7","P7"),"3.1.7":("Obj 7","P7"),
"3.2.1":("Obj 7","P2"),"3.2.2":("—","P2"),"3.2.3":("All (attestation)","P2"),"3.2.4":("Obj 7","P2"),"3.2.5":("Independent assessment","P2"),
"3.3.1":("Obj 5","—"),"3.3.2":("Obj 3","P7"),"3.3.3":("—","P4"),"3.3.4":("Obj 1","P7"),"3.3.5":("Obj 4, 5","P7"),
"3.3.6":("Obj 2","P7"),"3.3.7":("Obj 2","P7"),"3.3.8":("Obj 1, 2","P7"),"3.3.9":("Obj 2","P7"),"3.3.10":("—","P7"),
"3.3.11":("—","P7"),"3.3.12":("All","P7"),"3.3.13":("—","P7"),"3.3.14":("Obj 6","P7"),"3.3.15":("Obj 7","P6"),
"3.3.16":("Obj 7","P7"),"3.3.17":("Obj 2","P7"),
"3.4.1":("Obj 2","P5"),"3.4.2":("Obj 2","P5"),"3.4.3":("—","P5")}
SWIFT_OBJ=["1 Restrict Internet access and protect critical systems","2 Reduce attack surface and vulnerabilities","3 Physically secure the environment","4 Prevent compromise of credentials","5 Manage identities and segregate privileges","6 Detect anomalous activity","7 Plan for incident response and information sharing"]
BASEL_P=["P1 Governance","P2 Operational risk management","P3 Business continuity planning and testing","P4 Mapping of interconnections and interdependencies","P5 Third-party dependency management","P6 Incident management","P7 Resilient ICT including cyber security"]
