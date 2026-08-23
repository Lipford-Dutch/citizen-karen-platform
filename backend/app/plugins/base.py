class AgencyPlugin:
    def matches(self, data: dict) -> bool:
        raise NotImplementedError

    def forward(self, data: dict) -> dict:
        raise NotImplementedError
