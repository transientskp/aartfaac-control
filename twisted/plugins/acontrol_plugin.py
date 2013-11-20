from twisted.application.service import ServiceMaker

broker = ServiceMaker(
    "AARTFAAC Control", "acontrol.service", "The AARTFAAC Control System.", "acontrol"
)
