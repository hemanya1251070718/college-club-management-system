"""
Authoritative Club Memberships Catalog and Persona Governance Engine
Maps every student by student_id, PRN, or institutional email to their active club affiliations.
Supports multi-role personas (e.g., Secretary in CSI + Core Member in EDC + Member in Zephyr),
allowing students to select their active operating persona upon authentication.
"""

import os
import re

# Comprehensive canonical student memberships mapping across all 65 students and 105 active club roles
CANONICAL_STUDENT_MEMBERSHIPS = {
    "CE25-0369": [
        {
            "membership_id": "CSI-0369",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "President",
            "role_tier": "president",
            "join_date": "2025-08-05",
            "status": "Active"
        }
    ],
    "CE25-0718": [
        {
            "membership_id": "CSI-0718",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Secretary",
            "role_tier": "coordinator",
            "join_date": "2025-08-01",
            "status": "Active"
        },
        {
            "membership_id": "ZEPHYR-0718",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-20",
            "status": "Active"
        },
        {
            "membership_id": "MEM-EDC-CE250718",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2026-11-10",
            "status": "Active"
        }
    ],
    "CE25-1041": [
        {
            "membership_id": "CSI-1041",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Treasurer",
            "role_tier": "coordinator",
            "join_date": "2025-08-01",
            "status": "Active"
        },
        {
            "membership_id": "ZEPHYR-1041",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-01-10",
            "status": "Active"
        },
        {
            "membership_id": "EDC-1041",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-20",
            "status": "Active"
        }
    ],
    "EE25-0348": [
        {
            "membership_id": "CSI-0348",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Event Coordinator",
            "role_tier": "coordinator",
            "join_date": "2025-08-20",
            "status": "Active"
        },
        {
            "membership_id": "ZEPHYR-0348",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-03-05",
            "status": "Active"
        }
    ],
    "ME25-1053": [
        {
            "membership_id": "CSI-1053",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-09-10",
            "status": "Active"
        },
        {
            "membership_id": "SWD-1053",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-03-06",
            "status": "Active"
        }
    ],
    "CE25-0323": [
        {
            "membership_id": "CSI-0323",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Volunteer",
            "role_tier": "member",
            "join_date": "2025-08-05",
            "status": "Inactive"
        }
    ],
    "CE25-0277": [
        {
            "membership_id": "CSI-0277",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-09-15",
            "status": "Inactive"
        }
    ],
    "CE25-0314": [
        {
            "membership_id": "CSI-0314",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-09-15",
            "status": "Active"
        }
    ],
    "CE25-0152": [
        {
            "membership_id": "CSI-0152",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-01",
            "status": "Active"
        }
    ],
    "CE25-0804": [
        {
            "membership_id": "CSI-0804",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-05",
            "status": "Active"
        },
        {
            "membership_id": "SWD-0804",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-01-10",
            "status": "Active"
        }
    ],
    "CE25-0662": [
        {
            "membership_id": "CSI-0662",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-12",
            "status": "Active"
        }
    ],
    "CE25-0541": [
        {
            "membership_id": "CSI-0541",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2025-09-15",
            "status": "Active"
        },
        {
            "membership_id": "EDC-0541",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-02-05",
            "status": "Active"
        },
        {
            "membership_id": "ZEPHYR-0541",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-02-05",
            "status": "Active"
        }
    ],
    "CE25-0424": [
        {
            "membership_id": "CSI-0424",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Volunteer",
            "role_tier": "member",
            "join_date": "2025-08-12",
            "status": "Active"
        },
        {
            "membership_id": "ZEPHYR-0424",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-10-15",
            "status": "Active"
        }
    ],
    "CE25-0573": [
        {
            "membership_id": "CSI-0573",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-09-10",
            "status": "Active"
        }
    ],
    "CE25-0826": [
        {
            "membership_id": "CSI-0826",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Volunteer",
            "role_tier": "member",
            "join_date": "2025-09-01",
            "status": "Active"
        }
    ],
    "CE25-0998": [
        {
            "membership_id": "CSI-0998",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2025-09-10",
            "status": "Active"
        }
    ],
    "CE25-0870": [
        {
            "membership_id": "CSI-0870",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-12",
            "status": "Active"
        },
        {
            "membership_id": "EDC-0870",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-10-15",
            "status": "Active"
        },
        {
            "membership_id": "SWD-0870",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-01",
            "status": "Active"
        }
    ],
    "ME25-0893": [
        {
            "membership_id": "SWD-0893",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "President",
            "role_tier": "president",
            "join_date": "2025-08-10",
            "status": "Active"
        }
    ],
    "CE25-0431": [
        {
            "membership_id": "SWD-0431",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Secretary",
            "role_tier": "coordinator",
            "join_date": "2025-08-20",
            "status": "Active"
        }
    ],
    "CE25-0648": [
        {
            "membership_id": "SWD-0648",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Treasurer",
            "role_tier": "coordinator",
            "join_date": "2025-08-12",
            "status": "Active"
        },
        {
            "membership_id": "EDC-0648",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-01-10",
            "status": "Active"
        },
        {
            "membership_id": "CSI-0648",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-10-01",
            "status": "Active"
        }
    ],
    "CE25-0125": [
        {
            "membership_id": "SWD-0125",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Event Coordinator",
            "role_tier": "coordinator",
            "join_date": "2025-08-01",
            "status": "Active"
        },
        {
            "membership_id": "CSI-0125",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-20",
            "status": "Active"
        }
    ],
    "CE25-0453": [
        {
            "membership_id": "SWD-0453",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Volunteer",
            "role_tier": "member",
            "join_date": "2025-08-20",
            "status": "Active"
        },
        {
            "membership_id": "EDC-0453",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-01",
            "status": "Active"
        }
    ],
    "ME25-1059": [
        {
            "membership_id": "SWD-1059",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-12",
            "status": "Inactive"
        }
    ],
    "CE25-0855": [
        {
            "membership_id": "SWD-0855",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-12",
            "status": "Active"
        },
        {
            "membership_id": "EDC-0855",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-01-10",
            "status": "Active"
        }
    ],
    "CE25-0407": [
        {
            "membership_id": "SWD-0407",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2025-09-10",
            "status": "Active"
        },
        {
            "membership_id": "ZEPHYR-0407",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-20",
            "status": "Active"
        }
    ],
    "ELE25-0047": [
        {
            "membership_id": "SWD-0047",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-12",
            "status": "Active"
        },
        {
            "membership_id": "CSI-0047",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-10-15",
            "status": "Active"
        }
    ],
    "ME25-0898": [
        {
            "membership_id": "SWD-0898",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2025-09-10",
            "status": "Active"
        }
    ],
    "EE25-0757": [
        {
            "membership_id": "SWD-0757",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-09-10",
            "status": "Active"
        }
    ],
    "CE25-0150": [
        {
            "membership_id": "SWD-0150",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Volunteer",
            "role_tier": "member",
            "join_date": "2025-08-05",
            "status": "Active"
        },
        {
            "membership_id": "EDC-0150",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-03-03",
            "status": "Active"
        }
    ],
    "CE25-0493": [
        {
            "membership_id": "SWD-0493",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-01",
            "status": "Active"
        },
        {
            "membership_id": "EDC-0493",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-01-10",
            "status": "Active"
        }
    ],
    "ME25-0867": [
        {
            "membership_id": "SWD-0867",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Volunteer",
            "role_tier": "member",
            "join_date": "2025-09-15",
            "status": "Active"
        }
    ],
    "EE25-0246": [
        {
            "membership_id": "EDC-0246",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "President",
            "role_tier": "president",
            "join_date": "2024-08-01",
            "status": "Active"
        },
        {
            "membership_id": "CSI-0246",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-01",
            "status": "Active"
        }
    ],
    "CE25-0122": [
        {
            "membership_id": "EDC-0122",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Secretary",
            "role_tier": "coordinator",
            "join_date": "2025-08-05",
            "status": "Active"
        },
        {
            "membership_id": "SWD-0122",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-03-02",
            "status": "Active"
        }
    ],
    "CE25-0230": [
        {
            "membership_id": "EDC-0230",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Treasurer",
            "role_tier": "coordinator",
            "join_date": "2025-09-10",
            "status": "Active"
        },
        {
            "membership_id": "SWD-0230",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-10-01",
            "status": "Active"
        },
        {
            "membership_id": "ZEPHYR-0230",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-20",
            "status": "Active"
        }
    ],
    "CE25-1055": [
        {
            "membership_id": "EDC-1055",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Event Coordinator",
            "role_tier": "coordinator",
            "join_date": "2025-09-10",
            "status": "Active"
        }
    ],
    "CE25-0315": [
        {
            "membership_id": "EDC-0315",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2025-08-05",
            "status": "Active"
        }
    ],
    "CE25-1008": [
        {
            "membership_id": "EDC-1008",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-12",
            "status": "Active"
        }
    ],
    "CE25-0747": [
        {
            "membership_id": "EDC-0747",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-09-10",
            "status": "Active"
        },
        {
            "membership_id": "ZEPHYR-0747",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-10-01",
            "status": "Active"
        }
    ],
    "CE25-0226": [
        {
            "membership_id": "EDC-0226",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-09-10",
            "status": "Active"
        },
        {
            "membership_id": "CSI-0226",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-10-01",
            "status": "Active"
        }
    ],
    "CE25-0815": [
        {
            "membership_id": "EDC-0815",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2025-09-01",
            "status": "Active"
        },
        {
            "membership_id": "CSI-0815",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-02-05",
            "status": "Active"
        },
        {
            "membership_id": "ZEPHYR-0815",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-02-05",
            "status": "Active"
        }
    ],
    "CE25-0342": [
        {
            "membership_id": "EDC-0342",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-05",
            "status": "Active"
        }
    ],
    "EE25-0992": [
        {
            "membership_id": "EDC-0992",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-09-10",
            "status": "Active"
        }
    ],
    "CE25-0784": [
        {
            "membership_id": "EDC-0784",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Volunteer",
            "role_tier": "member",
            "join_date": "2025-08-12",
            "status": "Active"
        }
    ],
    "ELE25-0678": [
        {
            "membership_id": "EDC-0678",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-09-15",
            "status": "Active"
        }
    ],
    "CE25-0887": [
        {
            "membership_id": "EDC-0887",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2025-09-10",
            "status": "Active"
        },
        {
            "membership_id": "ZEPHYR-0887",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-10-01",
            "status": "Active"
        },
        {
            "membership_id": "SWD-0887",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-10-01",
            "status": "Active"
        }
    ],
    "CE25-0494": [
        {
            "membership_id": "EDC-0494",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Volunteer",
            "role_tier": "member",
            "join_date": "2025-09-15",
            "status": "Active"
        },
        {
            "membership_id": "SWD-0494",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-01",
            "status": "Active"
        }
    ],
    "EE25-1039": [
        {
            "membership_id": "EDC-1039",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-01",
            "status": "Active"
        },
        {
            "membership_id": "SWD-1039",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-10-01",
            "status": "Active"
        }
    ],
    "ME25-0187": [
        {
            "membership_id": "ZEPHYR-0187",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "President",
            "role_tier": "president",
            "join_date": "2025-09-15",
            "status": "Active"
        }
    ],
    "CE25-0193": [
        {
            "membership_id": "ZEPHYR-0193",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Secretary",
            "role_tier": "coordinator",
            "join_date": "2025-09-10",
            "status": "Active"
        },
        {
            "membership_id": "EDC-0193",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-03-04",
            "status": "Active"
        }
    ],
    "CE25-0311": [
        {
            "membership_id": "ZEPHYR-0311",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Treasurer",
            "role_tier": "coordinator",
            "join_date": "2025-08-20",
            "status": "Active"
        }
    ],
    "CE25-0203": [
        {
            "membership_id": "ZEPHYR-0203",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Event Coordinator",
            "role_tier": "coordinator",
            "join_date": "2025-09-10",
            "status": "Active"
        },
        {
            "membership_id": "EDC-0203",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-20",
            "status": "Active"
        }
    ],
    "CE25-1029": [
        {
            "membership_id": "ZEPHYR-1029",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-01",
            "status": "Active"
        },
        {
            "membership_id": "SWD-1029",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-01",
            "status": "Active"
        },
        {
            "membership_id": "EDC-1029",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-02-05",
            "status": "Active"
        }
    ],
    "CE25-0185": [
        {
            "membership_id": "ZEPHYR-0185",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-12",
            "status": "Active"
        }
    ],
    "ELE25-0416": [
        {
            "membership_id": "ZEPHYR-0416",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-09-15",
            "status": "Active"
        }
    ],
    "CE25-0112": [
        {
            "membership_id": "ZEPHYR-0112",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2025-08-01",
            "status": "Active"
        },
        {
            "membership_id": "CSI-0112",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-03-01",
            "status": "Active"
        }
    ],
    "ME25-0885": [
        {
            "membership_id": "ZEPHYR-0885",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Volunteer",
            "role_tier": "member",
            "join_date": "2025-09-01",
            "status": "Active"
        },
        {
            "membership_id": "EDC-0885",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2026-01-10",
            "status": "Active"
        }
    ],
    "CE25-0282": [
        {
            "membership_id": "ZEPHYR-0282",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-12",
            "status": "Active"
        }
    ],
    "CE25-1062": [
        {
            "membership_id": "ZEPHYR-1062",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Volunteer",
            "role_tier": "member",
            "join_date": "2025-08-20",
            "status": "Active"
        }
    ],
    "CE25-0307": [
        {
            "membership_id": "ZEPHYR-0307",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-01",
            "status": "Active"
        },
        {
            "membership_id": "SWD-0307",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-11-01",
            "status": "Active"
        }
    ],
    "CE25-0021": [
        {
            "membership_id": "CSI-0021",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2023-08-01",
            "status": "Active"
        }
    ],
    "EE25-0035": [
        {
            "membership_id": "EDC-0035",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2023-08-01",
            "status": "Active"
        }
    ],
    "ME25-0014": [
        {
            "membership_id": "SWD-0014",
            "club_id": "SWD",
            "club_name": "Social Welfare and Development Committee",
            "club_category": "Social Service",
            "role": "Core Member",
            "role_tier": "member",
            "join_date": "2023-08-01",
            "status": "Active"
        }
    ],
    "CE25-0042": [
        {
            "membership_id": "CSI-0042",
            "club_id": "CSI",
            "club_name": "Computer Society of India",
            "club_category": "Technical",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-10",
            "status": "Active"
        }
    ],
    "ELE25-0058": [
        {
            "membership_id": "EDC-0058",
            "club_id": "EDC",
            "club_name": "Entrepreneurship Development Club",
            "club_category": "Entrepreneurship",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-10",
            "status": "Active"
        }
    ],
    "ME25-0063": [
        {
            "membership_id": "ZEPHYR-0063",
            "club_id": "ZEPHYR",
            "club_name": "Zephyr",
            "club_category": "Dance",
            "role": "Member",
            "role_tier": "member",
            "join_date": "2025-08-10",
            "status": "Active"
        }
    ]
}

STUDENT_MEMBERSHIPS = CANONICAL_STUDENT_MEMBERSHIPS

def classify_role_tier(role_name):
    """
    Classifies raw role string into one of the 3 authorization tiers:
      - 'president': Club President
      - 'coordinator': Secretary, Coordinator, Treasurer, Lead, Event Coordinator
      - 'member': Member, Core Member, Volunteer
    """
    if not role_name:
        return 'member'
    r = role_name.strip().lower()
    if 'president' in r:
        return 'president'
    if any(k in r for k in ['secretary', 'coordinator', 'cordinator', 'treasurer', 'lead', 'head', 'vice president']):
        return 'coordinator'
    return 'member'

def get_persona_metadata(club_id, club_name, role_name, role_tier):
    """Generates rich display metadata for persona selection cards."""
    tier = role_tier or classify_role_tier(role_name)
    
    if tier == 'president':
        return {
            'tier': 'president',
            'tier_label': 'President Tier',
            'tier_badge_class': 'badge-status warning',
            'icon': 'bi-award-fill',
            'permissions_summary': 'Executive Governance: Single-president enforcement, budget allocations, and administrative oversight.'
        }
    elif tier == 'coordinator':
        return {
            'tier': 'coordinator',
            'tier_label': 'Coordinator Tier',
            'tier_badge_class': 'badge-status info',
            'icon': 'bi-person-badge-fill',
            'permissions_summary': 'Operations & Events: Schedule campus events, record check-in attendance, and manage student memberships.'
        }
    else:
        return {
            'tier': 'member',
            'tier_label': 'Member Tier',
            'tier_badge_class': 'badge-status neutral',
            'icon': 'bi-mortarboard-fill',
            'permissions_summary': 'Student Participant: Self-service event registrations, verified feedback reviews, and directory exploration.'
        }

def get_student_personas(student_id=None, prn=None, email=None):
    """
    Retrieves formatted list of available personas for a student.
    Returns: list of persona dicts with club details, role, authorization tier, and display badges.
    """
    mems = []
    if student_id and student_id in STUDENT_MEMBERSHIPS:
        mems = STUDENT_MEMBERSHIPS[student_id]
    elif prn:
        for sid, roles in STUDENT_MEMBERSHIPS.items():
            if sid.endswith(prn[-4:]) or prn in sid:
                mems = roles
                break
    elif email:
        email_clean = email.strip().lower()
        prn_match = re.search(r'\d{6,10}', email_clean)
        if prn_match:
            prn_str = prn_match.group(0)
            for sid, roles in STUDENT_MEMBERSHIPS.items():
                if sid.endswith(prn_str[-4:]) or prn_str in sid:
                    mems = roles
                    break

    personas = []
    for m in mems:
        tier = m.get('role_tier') or classify_role_tier(m.get('role', 'Member'))
        club_id = m.get('club_id', '')
        club_name = m.get('club_name', club_id)
        club_role = m.get('role', 'Member')
        meta = get_persona_metadata(club_id, club_name, club_role, tier)
        
        personas.append({
            'membership_id': m.get('membership_id'),
            'club_id': club_id,
            'club_name': club_name,
            'club_category': m.get('club_category', 'Charter'),
            'club_role': club_role,
            'role_tier': tier,
            'role_title': f'{club_role} — {club_name}',
            'tier_label': meta['tier_label'],
            'tier_badge_class': meta['tier_badge_class'],
            'icon': meta['icon'],
            'permissions_summary': meta['permissions_summary']
        })

    return personas
