from __future__ import annotations
from contextlib import ExitStack
from datetime import datetime
from enum import Enum
import json
from operator import attrgetter
import platform
import sys
from typing import Any, Dict, List, Optional, cast
from xmlrpc.client import ServerProxy
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import parse
from pydantic import BaseModel, Field, validator
import requests
from . import __url__, __version__
from .util import show_datetime

DEFAULT_ENDPOINT = "https://pypi.org/pypi"

USER_AGENT = "qypi/{} ({}) requests/{} {}/{}".format(
    __version__,
    __url__,
    requests.__version__,
    platform.python_implementation(),
    platform.python_version(),
)


class QyPI:
    def __init__(self, index_url: str = DEFAULT_ENDPOINT) -> None:
        self.index_url = index_url
        self.s = requests.Session()
        self.s.headers["User-Agent"] = USER_AGENT
        xsp_kwargs: dict[str, Any]
        if sys.version_info >= (3, 8):
            xsp_kwargs = {"headers": [("User-Agent", USER_AGENT)]}
        else:
            xsp_kwargs = {}
        self.xsp = ServerProxy(self.index_url, **xsp_kwargs)  # type: ignore[arg-type]
        self.ctx_stack = ExitStack()

    def __enter__(self) -> QyPI:
        self.ctx_stack.enter_context(self.s)
        self.ctx_stack.enter_context(self.xsp)
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.ctx_stack.close()

    def get_requirement(
        self,
        req: str,
        most_recent: bool = False,
        yanked: bool = False,
        prereleases: Optional[bool] = None,
    ) -> ProjectVersion:
        reqobj = Requirement(req)
        ### TODO: Warn if reqobj has non-None marker, extras, or url?
        project = self.get_project(reqobj.name)
        return project.get_version_by_spec(
            reqobj.specifier,
            most_recent=most_recent,
            yanked=yanked,
            prereleases=prereleases,
        )

    def get_all_requirements(
        self, req: str, yanked: bool = False, prereleases: Optional[bool] = None
    ) -> list[ProjectVersion]:
        reqobj = Requirement(req)
        ### TODO: Warn if reqobj has non-None marker, extras, or url?
        project = self.get_project(reqobj.name)
        return project.get_all_versions_by_spec(
            reqobj.specifier,
            yanked=yanked,
            prereleases=prereleases,
        )

    def get_project(self, project: str) -> Project:
        r = self.s.get(self.index_url.rstrip("/") + f"/{project}/json")
        if r.status_code == 404:
            raise QyPIError(f"{project}: project not found")
        r.raise_for_status()
        return Project.from_response_json(client=self, data=r.json())

    def get_project_version(self, project: str, version: str) -> ProjectVersion:
        r = self.s.get(self.index_url.rstrip("/") + f"/{project}/{version}/json")
        if r.status_code == 404:
            raise QyPIError(f"{project}: version {version} not found")
        r.raise_for_status()
        return ProjectVersion.from_response_json(r.json())

    def xmlrpc(self, method: str, *args: Any, **kwargs: Any) -> Any:
        return getattr(self.xsp, method)(*args, **kwargs)

    def list_all_projects(self) -> list[str]:
        return cast("list[str]", self.xmlrpc("list_packages"))

    def get_project_roles(self, project: str) -> list[ProjectRole]:
        return [
            ProjectRole(role=role, user=user)
            for role, user in self.xmlrpc("package_roles", project)
        ]

    def get_user_roles(self, user: str) -> list[UserRole]:
        return [
            UserRole(role=role, project=project)
            for role, project in self.xmlrpc("user_packages", user)
        ]

    def search(
        self, spec: dict[str, str | list[str]], operator: str = "and"
    ) -> list[SearchResult]:
        return [
            SearchResult.parse_obj(r) for r in self.xmlrpc("search", spec, operator)
        ]

    def browse(self, classifiers: list[str]) -> list[BrowseResult]:
        return [
            BrowseResult(name=name, version=version)
            for name, version in self.xmlrpc("browse", classifiers)
        ]


class QyPIError(Exception):
    pass


class Role(Enum):
    OWNER = "Owner"
    MAINTAINER = "Maintainer"


class JSONableBase(BaseModel):
    def json_dict(self, **kwargs: Any) -> dict:
        return cast(dict, json.loads(self.json(**kwargs)))


class ProjectRole(JSONableBase):
    user: str
    role: Role


class UserRole(JSONableBase):
    project: str
    role: Role


class SearchResult(JSONableBase):
    name: str
    summary: Optional[str]
    version: str

    @validator("summary")
    @classmethod
    def _nullify_summary(cls, v: Optional[str]) -> Optional[str]:
        if v == "" or v == "UNKNOWN":
            return None
        else:
            return v


class BrowseResult(JSONableBase):
    name: str
    version: str


class Downloads(JSONableBase):
    last_day: int
    last_month: int
    last_week: int


class ProjectInfo(JSONableBase):
    author: Optional[str]
    author_email: Optional[str]
    bugtrack_url: Optional[str]
    classifiers: List[str]
    description: Optional[str]
    description_content_type: Optional[str]
    docs_url: Optional[str]
    download_url: Optional[str]
    downloads: Downloads
    home_page: Optional[str]
    keywords: Optional[str]
    license: Optional[str]
    maintainer: Optional[str]
    maintainer_email: Optional[str]
    name: str
    package_url: str
    platform: Optional[str]
    project_url: str
    project_urls: Optional[Dict[str, str]]
    release_url: str
    requires_dist: Optional[List[str]]
    requires_python: Optional[str]
    summary: Optional[str]
    version: str
    yanked: bool
    yanked_reason: Optional[str]

    @validator(
        "author",
        "author_email",
        "bugtrack_url",
        "description",
        "description_content_type",
        "docs_url",
        "download_url",
        "downloads",
        "home_page",
        "keywords",
        "license",
        "maintainer",
        "maintainer_email",
        "platform",
        "requires_dist",
        "requires_python",
        "summary",
    )
    @classmethod
    def _nullify(cls, v: Optional[str]) -> Optional[str]:
        if v == "" or v == "UNKNOWN":
            return None
        else:
            return v


class ProjectFile(JSONableBase):
    comment_text: Optional[str]  # TODO: Nullify?
    digests: Dict[str, str]
    downloads: int
    filename: str
    has_sig: bool
    md5_digest: str
    packagetype: str
    python_version: str
    requires_python: Optional[str]
    size: int
    upload_time: datetime
    upload_time_iso_8601: datetime
    url: str
    yanked: bool
    yanked_reason: Optional[str]

    def json_dict(self, trust_downloads: bool = False, **kwargs: Any) -> dict:
        if not trust_downloads:
            kwargs.setdefault("exclude", set()).add("downloads")
        return super().json_dict(**kwargs)


class Vulnerability(JSONableBase):
    aliases: List[str]
    details: str
    fixed_in: List[str]
    id: str
    link: str
    source: str


class ProjectVersion(JSONableBase):
    info: ProjectInfo
    files: List[ProjectFile]
    vulnerabilities: List[Vulnerability]

    @classmethod
    def from_response_json(cls, data: dict) -> ProjectVersion:
        return cls(
            info=data["info"],
            files=data["urls"],
            vulnerabilities=data.get("vulnerabilities", []),
        )

    @property
    def name(self) -> str:
        return self.info.name

    @property
    def version(self) -> str:
        return self.info.version

    @property
    def upload_time(self) -> Optional[datetime]:
        return min((f.upload_time_iso_8601 for f in self.files), default=None)

    @property
    def is_yanked(self) -> bool:
        return self.info.yanked

    def qypi_json_dict(
        self, description: bool = False, trust_downloads: bool = False
    ) -> dict:
        info = self.info.json_dict(exclude_unset=True)
        if not description:
            info.pop("description", None)
        if not trust_downloads:
            info.pop("downloads", None)
        info["url"] = info.pop("home_page", None)
        info["release_date"] = show_datetime(self.upload_time)
        info["people"] = []
        for role in ("author", "maintainer"):
            name = info.pop(role, None)
            email = info.pop(role + "_email", None)
            if name or email:
                info["people"].append(
                    {
                        "name": name,
                        "email": email,
                        "role": role,
                    }
                )
        if "package_url" in info and "project_url" not in info:
            # Field was renamed between PyPI Legacy and Warehouse
            info["project_url"] = info.pop("package_url")
        return info


class Project(JSONableBase):
    client: QyPI = Field(exclude=True)
    default_version: ProjectVersion
    files: Dict[str, List[ProjectFile]]
    version_cache: Dict[str, ProjectVersion] = Field(
        default_factory=dict, exclude=True, repr=False
    )

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_response_json(cls, client: QyPI, data: dict) -> Project:
        default_version = ProjectVersion.from_response_json(data)
        return cls(
            client=client, default_version=default_version, files=data["releases"]
        )

    @property
    def name(self) -> str:
        return self.default_version.name

    @property
    def versions(self) -> list[str]:
        return list(self.files.keys())

    def get_version(self, version: str) -> ProjectVersion:
        if version not in self.version_cache:
            if version == self.default_version.version:
                v = self.default_version
            else:
                v = self.client.get_project_version(self.name, version)
            self.version_cache[version] = v
        return self.version_cache[version]

    def get_version_by_spec(
        self,
        spec: str | SpecifierSet,
        most_recent: bool = False,
        yanked: bool = False,
        prereleases: Optional[bool] = None,
    ) -> ProjectVersion:
        if not isinstance(spec, SpecifierSet):
            spec = SpecifierSet(spec)
        vs = list(spec.filter(self.versions, prereleases=prereleases))
        if most_recent:
            vobjs = [self.get_version(v) for v in vs]
            if not yanked:
                vobjs = [v for v in vobjs if not v.is_yanked]
            vobjs_uploaded = [v for v in vobjs if v.upload_time is not None]
            if vobjs_uploaded:
                return max(vobjs_uploaded, key=attrgetter("upload_time"))
            # else: Fallthrough to returning highest version
        vs.sort(key=parse, reverse=True)
        for v in vs:
            if yanked or not self.get_version(v).is_yanked:
                return self.get_version(v)
        raise QyPIError(f"{self.name}: no matching versions found")

    def get_all_versions_by_spec(
        self,
        spec: str | SpecifierSet,
        yanked: bool = False,
        prereleases: Optional[bool] = None,
    ) -> list[ProjectVersion]:
        if not isinstance(spec, SpecifierSet):
            spec = SpecifierSet(spec)
        vs = list(spec.filter(self.versions, prereleases=prereleases))
        vobjs = [self.get_version(v) for v in vs]
        if not yanked:
            vobjs = [v for v in vobjs if not v.is_yanked]
        return vobjs
