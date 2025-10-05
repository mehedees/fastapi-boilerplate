from ua_parser import user_agent_parser


class UserAgentUtil:
    @staticmethod
    def parse_user_agent(user_agent: str) -> dict:
        parsed = user_agent_parser.Parse(user_agent)
        return {
            "browser": f"{parsed['browser']['family']} - {parsed['browser']['version']}",
            "os": f"{parsed['os']['family']} - {parsed['os']['version']}",
            "device": f"{parsed['device']['family']} - {parsed['device']['brand']} - {parsed['device']['model']}",
        }
