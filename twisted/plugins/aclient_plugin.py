from twisted.application.service import ServiceMaker

broker = ServiceMaker(
    "AARTFAAC Client", "aclient.service", "The AARTFAAC Client System.", "aclient"
)
