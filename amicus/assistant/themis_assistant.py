from abc import ABC

from langchain.agents import load_tools
from langchain_community.chat_models import ChatOpenAI
from langchain.tools import BaseTool, StructuredTool, tool

from amicus.assistant.langchain_assistant import AgentAssistant
from typing import List, Dict

class DecisionElement(ABC):
    def __init__(self, id: str, initLevel: int, law: int = None  ):
        self.id = id
        self.initLevel = initLevel
        self.law = law

class Risk(DecisionElement):
    def __init__(self, id: str):
        DecisionElement.__init__(self, id, 0)
        self.parents = set()

    def declareParent ( self, parent: DecisionElement ):
        self.parents.add(parent)

    def evaluateLevel( self, levelValuation ) -> float:
        level = 0
        for p in self.parents:
            absScore = levelValuation.getLevel(p) * p.law
            if isinstance(p, Threat):
                level += absScore
            else:
                level -= absScore
        if level < 0:
            level = 0
        elif level > 1:
            level = 1
        return level


class Threat(DecisionElement):
    def __init__(self, id: str, level:float, law: int, risk: Risk  ):
        DecisionElement.__init__(self, id,level,law)
        self.risk = risk
        risk.declareParent(self)


class Mitigation(DecisionElement):
    def __init__(self, id: str, level:float, law: int, threat: Threat, risk: Risk  ):
        DecisionElement.__init__(self, id,level,law )
        self.risk = risk
        risk.declareParent(self)
        self.threat = threat


class LevelValuation:
    def __init__(self, elements: List[DecisionElement] ):
        self._element2level = dict()
        for e in elements:
            self._element2level[e] = e.initLevel

    def setRiskLevel ( self, risk: Risk) -> float:
        level = risk.evaluateLevel(self)
        self._element2level[risk] = level
        return risk

    def setThreatLevel(self, threat:Threat, level:float) -> float:
        self._element2level[threat] = level
        self.setRiskLevel( threat.risk )
        return level

    def setMitigationLevel(self, mitigation:Mitigation, level:float) -> float:
        self._element2level[mitigation] = level
        self.setRiskLevel( mitigation.risk )
        return level

    def setLevels ( self, levelValuation ):
        for e,l in levelValuation._element2level.items():
            self._element2level[e] = l

    def getLevel(self, element: DecisionElement) -> float:
        return self._element2level[element]

    def setLevels(self, levelValuation):
        for e, _ in self._element2level.items():
            self.setLevel( levelValuation.getLevel(e) )

    def findMitigationLevel(self, mitigation: Mitigation,
                            maxRiskLevel: float) -> float:
        oldMitigationLevel = self.getLevel(mitigation)
        ml = 1.0
        self.setMitigationLevel(mitigation, ml)
        riskLevel = self.getLevel( mitigation.risk )
        self.setMitigationLevel(mitigation, oldMitigationLevel)
        return None if riskLevel > maxRiskLevel else ml


class DecisionService:
    def __init__(self):
        self._risk = Risk( "Car blocked in traffic jam")
        self._threat = Threat ( "Period of high density traffic", .1, 2,
                                self._risk )
        self._mitigation = Mitigation ( "Find an alternative route with assistant", .1, 1,
                                        self._threat, self._risk )
        self._levelValuation = LevelValuation( [self._risk, self._threat, self._mitigation])

    def changeThreatLevel ( self, level: float ) -> float:
        return self._levelValuation.setThreatLevel(self._threat, level)

    def changeMitigationLevel(self, level: float) -> float:
        return self._levelValuation.setMitigationLevel(self._mitigation, level)

    def recommendMitigationLevel ( self, maxRiskLevel: float ) -> float:
        riskLevel = self._levelValuation.getLevel(self._risk)
        newLevel = None
        if ( riskLevel > maxRiskLevel):
            newLevel = self._levelValuation.findMitigationLevel( self._mitigation, maxRiskLevel )

        return newLevel

    def summeriseRiskLevel ( self) -> float:
        riskLevel = self._levelValuation.getLevel(self._risk)
        return riskLevel

decisionService = DecisionService()


@tool
def changeThreatLevel(level: float) -> float:
    """Change the threat level."""
    return decisionService.changeThreatLevel(level)


@tool
def changeMitigationLevel(level: float) -> float:
    """Change the mitigation level."""
    return decisionService.changeMitigationLevel(level)


@tool
def recommendMitigationLevel ( maxRiskLevel: float ) -> float:
    """Recommend the mitigation level to reduce a risk to a maximum value."""
    return decisionService.recommendMitigationLevel(maxRiskLevel)

@tool
def summeriseRiskLevel() -> float:
    """Summerise the risk levels."""
    return decisionService.summeriseRiskLevel()


class ThemisAssistant (AgentAssistant):
    def __init__(self, llm: ChatOpenAI, verbose: bool):
        AgentAssistant.__init__(self, llm, self._createTools(llm), verbose)

    @staticmethod
    def _createTools(llm):
        # tools = load_tools(["changeThreatLevel", "changeMitigationLevel", "recommendMitigationLevel", "summeriseRiskLevel"], llm=llm)
        tools = [changeThreatLevel, changeMitigationLevel, recommendMitigationLevel, summeriseRiskLevel]
        return tools