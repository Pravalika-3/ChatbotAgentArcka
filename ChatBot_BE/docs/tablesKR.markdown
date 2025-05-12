/****** Object:  Table [dbo].[FeedbackCriteria]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FeedbackCriteria](
	[FeedbackCriteriaID] [int] IDENTITY(1,1) NOT NULL,
	[FeedbackCriteria] [varchar](255) NULL,
	[IsDeleted] [bit] NULL,
	[CreatedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedDate] [datetime] NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsMandatory] [bit] NULL
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[vwGetFeedbackCriteriaForOtherSkills]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


CREATE View [dbo].[vwGetFeedbackCriteriaForOtherSkills] 
As 
	Select FeedbackCriteria,IsMandatory from FeedbackCriteria --WITH(NOLOCK)
	WHERE 
    IsMandatory = 0;
	--UNION
	--Select distinct FeedbackCriteria,IsCriteriaMandate from [dbo].FeedbackDetailsCriteria
GO
/****** Object:  Table [dbo].[UserRoleMapping]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[UserRoleMapping](
	[UserRoleMappingID] [int] IDENTITY(1,1) NOT NULL,
	[UserEmail] [varchar](255) NULL,
	[RoleID] [int] NULL,
	[CreatedDate] [datetime] NULL,
	[CreatedBy] [varchar](100) NULL,
	[UserName] [nvarchar](255) NOT NULL,
	[ModifiedDate] [date] NULL,
	[ModifiedBy] [varchar](55) NULL,
	[IsActive] [bit] NULL
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[vwGetRecuiters]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW  [dbo].[vwGetRecuiters] AS
SELECT 
    UserRoleMappingID,
    UserEmail,
    RoleID,
    UserName
FROM [dbo].[UserRoleMapping]
WHERE RoleID = 2 OR RoleID=1;
GO
/****** Object:  Table [dbo].[JobDescription]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[JobDescription](
	[JobDescriptionId] [int] IDENTITY(1,1) NOT NULL,
	[DesignationID] [int] NOT NULL,
	[SkillsId] [int] NOT NULL,
	[JobDescription] [varchar](4000) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[JobDescriptionId] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Designation]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Designation](
	[DesignationID] [int] IDENTITY(1,1) NOT NULL,
	[Designation] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[DesignationID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Skills]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Skills](
	[SkillsID] [int] IDENTITY(1,1) NOT NULL,
	[Skills] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[SkillsID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[vwGetJobDescriptionDetails]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


CREATE VIEW [dbo].[vwGetJobDescriptionDetails]
AS
SELECT DISTINCT
	JD.JobDescriptionId,
	JT.DesignationID,
	JT.Designation,
	SK.SkillsID,
	SK.Skills,
	JD.JobDescription,
	JD.CreatedDate,
	JD.ModifiedDate,
	CASE 
            WHEN CHARINDEX('@',JD.CreatedBy) > 0 THEN 
                LEFT(JD.CreatedBy, CHARINDEX('@', JD.CreatedBy) - 1)
            ELSE JD.CreatedBy 
        END AS CreatedBy,
	CASE 
            WHEN CHARINDEX('@', JD.ModifiedBy) > 0 THEN
                LEFT(JD.ModifiedBy, CHARINDEX('@', JD.ModifiedBy) - 1)
            ELSE JD.ModifiedBy 
        END AS ModifiedBy,
	JD.isDeleted
FROM
	[dbo].[JobDescription] JD,
	[dbo].[Designation] JT,
	[dbo].[Skills] SK
WHERE
	JD.DesignationID = JT.DesignationID AND
	JD.SkillsId = SK.SkillsID
GO
/****** Object:  Table [dbo].[Roles]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Roles](
	[RoleID] [int] IDENTITY(1,1) NOT NULL,
	[RoleName] [varchar](255) NULL,
	[CreatedDate] [datetime] NULL,
	[CreatedBy] [varchar](100) NULL
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[vwGetInterviewers]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

Create View [dbo].[vwGetInterviewers] As
	Select UserName from [dbo].[UserRoleMapping] where RoleId in (
		Select RoleID from Roles where RoleName='[dbo].[UserRoleMapping]')
GO
/****** Object:  Table [dbo].[SourcingForm]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[SourcingForm](
	[SourcingFormID] [int] IDENTITY(1,1) NOT NULL,
	[RequestFormID] [int] NULL,
	[RequisitionID] [varchar](100) NOT NULL,
	[HiringForId] [int] NOT NULL,
	[SkillsID] [int] NOT NULL,
	[SubSkills] [varchar](255) NOT NULL,
	[SkillSetRating] [int] NOT NULL,
	[PointOfContactID] [int] NOT NULL,
	[CandidateName] [varchar](255) NOT NULL,
	[MobileNumber] [varchar](20) NOT NULL,
	[Email] [varchar](255) NOT NULL,
	[EducationID] [int] NOT NULL,
	[CurrentOrganization] [varchar](255) NOT NULL,
	[TotalExperience] [decimal](15, 2) NOT NULL,
	[ReleventExperience] [decimal](15, 2) NOT NULL,
	[CurrentLocation] [varchar](255) NOT NULL,
	[PreferredLocationID] [int] NOT NULL,
	[CTC] [decimal](15, 2) NULL,
	[ECTC] [decimal](15, 2) NULL,
	[IfHoldingOfferCTCAndOrganizationName] [varchar](2000) NULL,
	[OfficialNoticePeriodID] [int] NOT NULL,
	[IfServingNoticeLWD] [datetime] NULL,
	[Comment] [varchar](4000) NULL,
	[CommunicationRating] [int] NOT NULL,
	[ResumeURL] [varchar](2000) NOT NULL,
	[ScreeningDateTime] [datetime] NULL,
	[ScreeningPanel] [varchar](200) NULL,
	[ScreeningStatusID] [int] NULL,
	[T1Date] [datetime] NULL,
	[T1Panel] [varchar](255) NULL,
	[T1StatusID] [int] NULL,
	[T2Date] [datetime] NULL,
	[T2Panel] [varchar](255) NULL,
	[T2StatusID] [int] NULL,
	[HRDate] [datetime] NULL,
	[HRPanel] [varchar](255) NULL,
	[HRStatusID] [int] NULL,
	[StatusRemark] [varchar](1000) NULL,
	[Remarks] [varchar](1000) NULL,
	[DOJ] [datetime] NULL,
	[WorkingStatusID] [int] NULL,
	[IsActive] [bit] NOT NULL,
	[CreatedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedDate] [datetime] NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
	[Recruiter] [varchar](255) NULL,
	[RecruiterEmail] [varchar](255) NULL,
	[RequestStatus] [varchar](100) NULL,
	[CurrentStatus] [varchar](1000) NULL,
	[IsMigratedData] [bit] NULL,
	[IsDataConsideredForReport] [bit] NULL,
	[Age] [int] NULL,
	[Gender] [varchar](50) NULL,
	[HouseLocation] [varchar](255) NULL,
	[HouseToWorkLocationDistance] [decimal](10, 2) NULL,
	[YearsInCurrentWorkLocation] [int] NULL,
	[MaritalStatus] [varchar](50) NULL,
	[Kids] [int] NULL,
	[SpokenLanguage] [varchar](255) NULL,
	[NoOfOffersInHand] [int] NULL,
	[CurrentWorkingStatus] [varchar](255) NULL,
	[MonthsNotWorking] [int] NULL,
	[IsResourceHybridOrWFH] [bit] NULL,
	[IsCandidateFlagged] [bit] NULL,
	[FlaggedReason] [varchar](1000) NULL,
	[CurrentCompanyType] [varchar](255) NULL,
	[ReasonForLeavingCompany] [varchar](1000) NULL,
	[NoOfYearsInCurrentCompany] [int] NULL,
	[NoOfCompaniesYearsOfExperience] [int] NULL,
	[IsReferral] [bit] NULL,
	[ReferenceType] [varchar](255) NULL,
	[ReferralName] [varchar](255) NULL,
PRIMARY KEY CLUSTERED 
(
	[SourcingFormID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[vwGetCandidateDetails]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE View [dbo].[vwGetCandidateDetails] As
	Select RequisitionID, CandidateName,WorkingStatusID from dbo.SourcingForm
GO
/****** Object:  Table [dbo].[RequestForm]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RequestForm](
	[RequestFormID] [int] IDENTITY(1,1) NOT NULL,
	[RequisitionID] [varchar](100) NOT NULL,
	[RequisitionTypeID] [int] NOT NULL,
	[RequestRaisedForID] [int] NOT NULL,
	[RequestorName] [varchar](255) NOT NULL,
	[VacancyReasonID] [int] NOT NULL,
	[DesignationID] [int] NOT NULL,
	[PositionPriorityID] [int] NOT NULL,
	[JobDescription] [varchar](max) NOT NULL,
	[EmployeeTypeID] [int] NOT NULL,
	[WorkLocationID] [int] NOT NULL,
	[ReportingStructure] [varchar](2000) NOT NULL,
	[RecruitmentProcessID] [int] NOT NULL,
	[IsSendEmailForResponse] [bit] NULL,
	[IsActive] [bit] NULL,
	[CreatedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedDate] [datetime] NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NULL,
	[RequestStatus] [varchar](100) NULL,
	[ExpectedCompletionDate] [datetime] NULL,
	[RequestCompletionDate] [datetime] NULL,
	[SkillsId] [int] NULL,
	[HiringForID] [int] NULL,
	[IsMigratedData] [bit] NULL,
	[IsDataConsideredForReport] [bit] NULL,
PRIMARY KEY CLUSTERED 
(
	[RequestFormID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RequisitionType]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RequisitionType](
	[RequisitionTypeID] [int] IDENTITY(1,1) NOT NULL,
	[RequisitionType] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[RequisitionTypeID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RequestRaisedFor]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RequestRaisedFor](
	[RequestRaisedForID] [int] IDENTITY(1,1) NOT NULL,
	[RequestRaisedFor] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[RequestRaisedForID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[VacancyReason]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[VacancyReason](
	[VacancyReasonID] [int] IDENTITY(1,1) NOT NULL,
	[VacancyReason] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[VacancyReasonID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PositionPriority]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PositionPriority](
	[PositionPriorityID] [int] IDENTITY(1,1) NOT NULL,
	[PositionPriority] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[PositionPriorityID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[WorkLocation]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[WorkLocation](
	[WorkLocationID] [int] IDENTITY(1,1) NOT NULL,
	[WorkLocation] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[WorkLocationID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[EmployeeType]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[EmployeeType](
	[EmployeeTypeID] [int] IDENTITY(1,1) NOT NULL,
	[EmployeeType] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[EmployeeTypeID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RecruitmentProcess]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RecruitmentProcess](
	[RecruitmentProcessID] [int] IDENTITY(1,1) NOT NULL,
	[RecruitmentProcess] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[RecruitmentProcessID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[HiringFor]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[HiringFor](
	[HiringForID] [int] IDENTITY(1,1) NOT NULL,
	[HiringFor] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
	[ProjectStatus] [varchar](50) NULL,
PRIMARY KEY CLUSTERED 
(
	[HiringForID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[vwGetRequestForm]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO





CREATE VIEW [dbo].[vwGetRequestForm] AS 
SELECT 
	a.RequestFormID,
	a.RequisitionID,
	a.RequisitionTypeID,
	rt.RequisitionType,
	a.RequestRaisedForID,
	rr.RequestRaisedFor,
	a.RequestorName,
	a.SkillsId,
	jt.Skills,
	a.VacancyReasonID,
	vr.VacancyReason,
	a.DesignationID,
	d.Designation,
	a.PositionPriorityID,
	pp.PositionPriority,
	a.HiringForID,
	hf.HiringFor,
	a.JobDescription,
	a.EmployeeTypeID,
	et.EmployeeType,
	a.WorkLocationID,
	wl.WorkLocation,
	a.ReportingStructure,
	a.RecruitmentProcessID,
	rp.RecruitmentProcess,
	a.IsSendEmailForResponse,
	a.IsActive,
	a.RequestStatus,
	a.RequestCompletionDate,
	a.ExpectedCompletionDate,
	a.CreatedDate,
--	a.CreatedBy,
  CASE 
        WHEN CHARINDEX('@', a.CreatedBy) > 0 THEN 
		LEFT(a.CreatedBy, CHARINDEX('@', a.CreatedBy) - 1)
        ELSE a.CreatedBy END AS CreatedBy,

	a.ModifiedDate,
--	a.ModifiedBy,

  CASE 
		WHEN CHARINDEX('@', a.ModifiedBy) > 0 THEN
		LEFT(a.ModifiedBy, CHARINDEX('@' , a.ModifiedBy) -1)
		ELSE a.ModifiedBy END AS ModifiedBy,


	a.IsDeleted
FROM 
	dbo.RequestForm a WITH(NOLOCK) 
INNER JOIN 
	dbo.RequisitionType rt WITH(NOLOCK) on rt.RequisitionTypeID=a.RequisitionTypeID
INNER JOIN
	dbo.RequestRaisedFor rr WITH(NOLOCK) on rr.RequestRaisedForID=a.RequestRaisedForID
INNER JOIN
	dbo.Skills jt WITH(NOLOCK) on jt.SkillsID=a.SkillsId
INNER JOIN
	dbo.VacancyReason vr WITH(NOLOCK) on vr.VacancyReasonID=a.VacancyReasonID
INNER JOIN
	dbo.Designation d WITH(NOLOCK) on d.DesignationID=a.DesignationID
INNER JOIN
	dbo.PositionPriority pp WITH(NOLOCK) on pp.PositionPriorityID=a.PositionPriorityID
INNER JOIN
	dbo.EmployeeType et WITH(NOLOCK) on et.EmployeeTypeID=a.EmployeeTypeID
INNER JOIN
	dbo.WorkLocation wl WITH(NOLOCK) on wl.WorkLocationID=a.WorkLocationID
INNER JOIN
	dbo.RecruitmentProcess rp WITH(NOLOCK) on rp.RecruitmentProcessID=a.RecruitmentProcessID
	INNER JOIN
	dbo.HiringFor hf WITH(NOLOCK) on hf.HiringForID=a.HiringForID
GO
/****** Object:  Table [dbo].[Education]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Education](
	[EducationID] [int] IDENTITY(1,1) NOT NULL,
	[Education] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[EducationID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PreferredLocation]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PreferredLocation](
	[PreferredLocationID] [int] IDENTITY(1,1) NOT NULL,
	[PreferredLocation] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[PreferredLocationID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[OfficialNoticePeriod]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[OfficialNoticePeriod](
	[OfficialNoticePeriodID] [int] IDENTITY(1,1) NOT NULL,
	[OfficialNoticePeriod] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[OfficialNoticePeriodID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[PointOfContact]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[PointOfContact](
	[PointOfContactID] [int] IDENTITY(1,1) NOT NULL,
	[PointOfContact] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[PointOfContactID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[InterviewStatus]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[InterviewStatus](
	[InterviewStatusID] [int] IDENTITY(1,1) NOT NULL,
	[InterviewStatusType] [varchar](255) NOT NULL,
	[InterviewStatus] [varchar](255) NOT NULL,
	[CreatedDate] [datetime] NULL,
	[ModifiedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedBy] [varchar](255) NULL,
	[IsDeleted] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[InterviewStatusID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[vwGetSourcingForm]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

  
  
  
  
CREATE VIEW [dbo].[vwGetSourcingForm] AS  
SELECT   
 a.SourcingFormID,  
 a.RequestFormID,  
 a.RequisitionID,  
 a.HiringForId,  
 hf.HiringFor,  
 a.SkillsID,  
 s.Skills,  
 a.SubSkills,  
 a.SkillSetRating,  
 a.PointOfContactID,  
 pc.PointOfContact,  
 a.CandidateName,  
 a.MobileNumber,  
 a.Email,  
 a.EducationID,  
 e.Education,  
 a.CurrentOrganization,  
 a.TotalExperience,  
 a.ReleventExperience,  
 a.CurrentLocation,  
 a.PreferredLocationID,  
 pl.PreferredLocation,  
 a.CTC,  
 a.ECTC,  
 a.IfHoldingOfferCTCAndOrganizationName,  
 a.OfficialNoticePeriodID,  
 onp.OfficialNoticePeriod,  
 a.IfServingNoticeLWD,  
 a.Comment,  
 a.CommunicationRating,  
 a.ResumeURL,  
 a.ScreeningPanel,  
 a.ScreeningDateTime ScreeningDate,  
 a.ScreeningStatusID,  
 is1.InterviewStatus ScreeningStatus,  
 a.T1Date,  
 a.T1Panel,  
 a.T1StatusID,   
 is2.InterviewStatus T1Status,  
 a.T2Date,  
 a.T2Panel,  
 a.T2StatusID,  
 is3.InterviewStatus T2Status,  
 a.HRDate,  
 a.HRPanel,  
 a.HRStatusID,  
 is4.InterviewStatus HRStatus,  
 a.CurrentStatus,  
 a.StatusRemark,  
 a.Remarks,  
 a.DOJ,  
 a.WorkingStatusID,  
 is6.InterviewStatus WorkingStatus,  
 case when remarks='joined' then 1 else 0 end IsJoined,  
  a.IsActive,  
 HiringDays= DateDiff(DAY,[DOJ] ,[ScreeningDateTime]),  
 a.CreatedDate,  
 a.CreatedBy,  
 a.ModifiedDate,  
 a.ModifiedBy,  
 a.IsDeleted,  
 a.Recruiter,  
 a.RecruiterEmail,  
 a.RequestStatus  
FROM   
 dbo.SourcingForm a WITH(NOLOCK)   
INNER JOIN   
 dbo.RequestForm rf WITH(NOLOCK) on rf.RequestFormID=a.RequestFormID  
INNER JOIN  
 dbo.HiringFor hf WITH(NOLOCK) on hf.HiringForId=a.HiringForId  
INNER JOIN  
 dbo.Skills s WITH(NOLOCK) on s.SkillsID=a.SkillsID  
INNER JOIN  
 dbo.PointOfContact pc WITH(NOLOCK) on pc.PointOfContactID=a.PointOfContactID  
INNER JOIN  
 dbo.Education e WITH(NOLOCK) on e.EducationID=a.EducationID  
INNER JOIN  
 dbo.PreferredLocation pl WITH(NOLOCK) on pl.PreferredLocationID=a.PreferredLocationID  
INNER JOIN  
 dbo.OfficialNoticePeriod onp WITH(NOLOCK) on onp.OfficialNoticePeriodID=a.OfficialNoticePeriodID  
LEFT OUTER JOIN  
 dbo.InterviewStatus is1 WITH(NOLOCK) on is1.InterviewStatusId=a.ScreeningStatusID  
LEFT OUTER JOIN  
 dbo.InterviewStatus is2 WITH(NOLOCK) on is2.InterviewStatusId=a.T1StatusID   
LEFT OUTER JOIN  
 dbo.InterviewStatus is3 WITH(NOLOCK) on is3.InterviewStatusId=a.T2StatusID   
LEFT OUTER JOIN  
 dbo.InterviewStatus is4 WITH(NOLOCK) on is4.InterviewStatusId=a.HRStatusID   
LEFT OUTER JOIN  
 dbo.InterviewStatus is6 WITH(NOLOCK) on is6.InterviewStatusId=a.WorkingStatusID  
GO
/****** Object:  Table [dbo].[FeedbackDetailsCriteria]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FeedbackDetailsCriteria](
	[FeedbackDetailsCriteriaID] [int] IDENTITY(1,1) NOT NULL,
	[FeedbackDetailsID] [int] NULL,
	[FeedbackCriteria] [varchar](255) NULL,
	[Rating] [numeric](5, 2) NULL,
	[IsCriteriaMandate] [bit] NULL,
	[DisplayOrder] [int] NULL,
	[FeedbackStatus] [varchar](100) NULL,
	[IsDeleted] [bit] NULL,
	[CreatedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedDate] [datetime] NULL,
	[ModifiedBy] [varchar](255) NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[FeedbackDetails]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[FeedbackDetails](
	[FeedbackDetailsID] [int] IDENTITY(1,1) NOT NULL,
	[RequestFormID] [int] NULL,
	[SourcingFormID] [int] NULL,
	[InterviewerName] [varchar](500) NULL,
	[InterviewLevel] [varchar](100) NULL,
	[InterviewStatus] [varchar](100) NULL,
	[OtherComments] [varchar](5000) NULL,
	[IsDeleted] [bit] NULL,
	[CreatedDate] [datetime] NULL,
	[CreatedBy] [varchar](255) NULL,
	[ModifiedDate] [datetime] NULL,
	[ModifiedBy] [varchar](255) NULL,
	[CandidateName] [varchar](max) NULL,
	[MobileNumber] [varchar](20) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  View [dbo].[vwGetFeedbackDetails]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE View [dbo].[vwGetFeedbackDetails] 
As
Select Distinct fd.FeedbackDetailsID,r.RequestFormID,r.RequisitionID,fd.InterviewerName,fd.InterviewStatus,
sf.SourcingFormID,sf.CandidateName,OtherComments
from 
dbo.FeedbackDetails fd 
inner join dbo.RequestForm r on fd.RequestFormID = r.RequestFormID
inner join dbo.SourcingForm sf on sf.SourcingFormID = fd.SourcingFormID
left outer join dbo.FeedbackDetailsCriteria fdc on fdc.FeedbackDetailsID=fd.FeedbackDetailsID
GO
/****** Object:  View [dbo].[vwGetRequestFormReport]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO



 CREATE   VIEW [dbo].[vwGetRequestFormReport] AS   
  
With cteSourcingForm as (  
 Select * from (  
 Select RequisitionID, dense_rank()over(partition by RequisitionID order by  
  case when remarks='joined' or HrStatusId=33 then 1 else 0 end desc,[DOJ] desc,  
  SourcingFormId asc)rnk,[DOJ]  
 FROM   
  dbo.SourcingForm  
 )a where Rnk=1  
) ,cteRemarks as (
SELECT     
 a.RequisitionID, STRING_AGG(concat(a.CandidateName,'[',case when is4.InterviewStatus ='HR Select' then 'HR' when  is3.InterviewStatus='T2 Select'
 then 'T2' end,'-',is6.InterviewStatus,'-',ISNULL(FORMAT(a.DOJ, 'dd/MM/yyyy'), ''),'-',Remarks,']'),CHAR(10))  AllRemarks
FROM     
 dbo.SourcingForm a WITH(NOLOCK)     
INNER JOIN     
 dbo.RequestForm rf WITH(NOLOCK) on rf.RequestFormID=a.RequestFormID    
LEFT OUTER JOIN    
 dbo.InterviewStatus is3 WITH(NOLOCK) on is3.InterviewStatusId=a.T2StatusID     
LEFT OUTER JOIN    
 dbo.InterviewStatus is4 WITH(NOLOCK) on is4.InterviewStatusId=a.HRStatusID     
LEFT OUTER JOIN    
 dbo.InterviewStatus is6 WITH(NOLOCK) on is6.InterviewStatusId=a.WorkingStatusID    
WHERE  
 a.IsDataConsideredForReport=1 AND (is3.InterviewStatus='T2 Select' OR is4.InterviewStatus='HR Select'
 OR  is6.InterviewStatus in ('Document Collection','Offer Released','Onboarded','Select')
 ) and a.CreatedDate >= DATEADD(WEEK, -1, GETDATE())
  AND a.CreatedDate < GETDATE() 
 group by a.RequisitionID
 )
SELECT   
 a.RequestFormID,  
 a.RequisitionID,  
 a.RequisitionTypeID,  
 rt.RequisitionType,  
 a.RequestRaisedForID,  
 rr.RequestRaisedFor,  
 a.RequestorName,  
 a.SkillsId,  
 jt.Skills,  
 a.VacancyReasonID,  
 case when vr.VacancyReason like '%Replacement%' then 'Replacement'
 when vr.VacancyReason like '%New%' then 'New Vacancy'
 else VacancyReason end VacancyReason,  
 a.DesignationID,  
 d.Designation,  
 a.PositionPriorityID,  
 pp.PositionPriority,  
 a.HiringForID,  
 hf.HiringFor,  
 a.JobDescription,  
 a.EmployeeTypeID,  
 et.EmployeeType,  
 a.WorkLocationID,  
 wl.WorkLocation,  
 a.ReportingStructure,  
 a.RecruitmentProcessID,  
 rp.RecruitmentProcess,  
 a.IsSendEmailForResponse,  
 a.IsActive,  
 a.RequestStatus,  
 a.RequestCompletionDate,  
 a.ExpectedCompletionDate,  
 cast(a.CreatedDate as date) CreatedDate,  
 a.CreatedBy,  
 a.ModifiedDate,  
 a.ModifiedBy,  
 a.IsDeleted,  
 [DOJ],  
 Age=case
 when RequestStatus='InProgress'  and DOJ is null then
	DATEDIFF(DAY,a.CreatedDate,ISNULL([DOJ],getdate()))
 else
	null
 end,
 RemainingDays = case 
	when RequestStatus='InProgress' and DOJ is null then  
		DATEDIFF(DAY,getdate(),ExpectedCompletionDate)
	else 
		null 	
 end,  
 DaysSetForCompletion = DATEDIFF(DAY,a.CreatedDate,ExpectedCompletionDate),  
 case when a.RequestStatus<>'InProgress' then 'Closed Position' else 'Open Position' end Positions ,
 r.AllRemarks Remarks
FROM   
 dbo.RequestForm a WITH(NOLOCK)   
INNER JOIN   
 dbo.RequisitionType rt WITH(NOLOCK) on rt.RequisitionTypeID=a.RequisitionTypeID  
INNER JOIN  
 dbo.RequestRaisedFor rr WITH(NOLOCK) on rr.RequestRaisedForID=a.RequestRaisedForID  
INNER JOIN  
 dbo.Skills jt WITH(NOLOCK) on jt.SkillsID=a.SkillsId  
INNER JOIN  
 dbo.VacancyReason vr WITH(NOLOCK) on vr.VacancyReasonID=a.VacancyReasonID  
INNER JOIN  
 dbo.Designation d WITH(NOLOCK) on d.DesignationID=a.DesignationID  
INNER JOIN  
 dbo.PositionPriority pp WITH(NOLOCK) on pp.PositionPriorityID=a.PositionPriorityID  
INNER JOIN  
 dbo.EmployeeType et WITH(NOLOCK) on et.EmployeeTypeID=a.EmployeeTypeID  
INNER JOIN  
 dbo.WorkLocation wl WITH(NOLOCK) on wl.WorkLocationID=a.WorkLocationID  
INNER JOIN  
 dbo.RecruitmentProcess rp WITH(NOLOCK) on rp.RecruitmentProcessID=a.RecruitmentProcessID  
INNER JOIN  
 dbo.HiringFor hf WITH(NOLOCK) on hf.HiringForID=a.HiringForID 
LEFT OUTER JOIN   
 cteSourcingForm cf on cf.RequisitionID=a.RequisitionID  
LEFT OUTER JOIN		
	cteRemarks r on r.RequisitionID=a.RequisitionID
WHERE  
 a.IsDataConsideredForReport=1
GO
/****** Object:  View [dbo].[vwGetSourcingFormReport]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
  
  
  
  
CREATE VIEW [dbo].[vwGetSourcingFormReport] AS    
SELECT     
 a.SourcingFormID,    
 a.RequestFormID,    
 a.RequisitionID,    
 a.HiringForId,    
 hf.HiringFor,    
 a.SkillsID,    
 s.Skills,    
 a.SubSkills,    
 a.SkillSetRating,    
 a.PointOfContactID,    
 pc.PointOfContact,    
 a.CandidateName,    
 a.MobileNumber,    
 a.Email,    
 a.EducationID,    
 e.Education,    
 a.CurrentOrganization,    
 a.TotalExperience,    
 a.ReleventExperience,    
 a.CurrentLocation,    
 a.PreferredLocationID,    
 pl.PreferredLocation,    
 a.CTC,    
 a.ECTC,    
 a.IfHoldingOfferCTCAndOrganizationName,    
 a.OfficialNoticePeriodID,    
 onp.OfficialNoticePeriod,    
 a.IfServingNoticeLWD,    
 a.Comment,    
 a.CommunicationRating,    
 a.ResumeURL,    
 a.ScreeningPanel,    
 cast(a.ScreeningDateTime as date) ScreeningDate,    
 a.ScreeningStatusID,    
 is1.InterviewStatus ScreeningStatus,    
 cast(a.T1Date as date) T1Date,    
 a.T1Panel,    
 a.T1StatusID,     
 is2.InterviewStatus T1Status,    
 cast(a.T2Date as date) T2Date,    
 a.T2Panel,    
 a.T2StatusID,    
 is3.InterviewStatus T2Status,    
 cast(a.HRDate  as date) HRDate,    
 a.HRPanel,    
 a.HRStatusID,    
 is4.InterviewStatus HRStatus,    
 a.CurrentStatus,    
 a.StatusRemark,    
 a.Remarks,    
 a.DOJ,    
 a.WorkingStatusID,    
 is6.InterviewStatus WorkingStatus,    
 case when rf.RequestStatus<>'InProgress' then 'Closed Position' else 'Open Position' end Positions,    
 case when a.RequestStatus='Onboarded' then 1 else 0 end IsJoined,    
 case when ScreeningStatusID is not null then 1 else 0 end TotalScreened,    
 case when is1.InterviewStatus='Screen Select' then 1 else 0 end TotalScreenSelect,    
 case when T1StatusID is not null then 1 else 0 end TotalT1,    
 case when is2.InterviewStatus='T1 Select' then 1 else 0 end TotalT1Select,    
 case when T2StatusID is not null then 1 else 0 end TotalT2,    
 case when is3.InterviewStatus='T2 Select' then 1 else 0 end TotalT2Select,    
 case when HRStatusID is not null then 1 else 0 end TotalHR,    
 case when is4.InterviewStatus='HR Select' then 1 else 0 end TotalHRSelect,   
 case when is6.InterviewStatus='Onboarded' then 1 else 0 end TotalHROnboarded,
 case when is6.InterviewStatus='Document Collection' then 1 else 0 end TotalDocumentCollection, 
 case when is6.InterviewStatus='Offer Released' then 1 else 0 end TotalOfferReleased, 
  a.IsActive,    
 HiringDays= DateDiff(DAY,[ScreeningDateTime],[DOJ]),    
 cast(a.CreatedDate as date) CreatedDate,    
 a.CreatedBy,    
 a.ModifiedDate,    
 a.ModifiedBy,    
 a.IsDeleted,    
 a.Recruiter,    
 a.RecruiterEmail,  
 rf.RequestStatus 
FROM     
 dbo.SourcingForm a WITH(NOLOCK)     
INNER JOIN     
 dbo.RequestForm rf WITH(NOLOCK) on rf.RequestFormID=a.RequestFormID    
INNER JOIN    
 dbo.HiringFor hf WITH(NOLOCK) on hf.HiringForId=a.HiringForId    
INNER JOIN    
 dbo.Skills s WITH(NOLOCK) on s.SkillsID=a.SkillsID    
INNER JOIN    
 dbo.PointOfContact pc WITH(NOLOCK) on pc.PointOfContactID=a.PointOfContactID    
INNER JOIN    
 dbo.Education e WITH(NOLOCK) on e.EducationID=a.EducationID    
INNER JOIN    
 dbo.PreferredLocation pl WITH(NOLOCK) on pl.PreferredLocationID=a.PreferredLocationID    
INNER JOIN    
 dbo.OfficialNoticePeriod onp WITH(NOLOCK) on onp.OfficialNoticePeriodID=a.OfficialNoticePeriodID    
LEFT OUTER JOIN    
 dbo.InterviewStatus is1 WITH(NOLOCK) on is1.InterviewStatusId=a.ScreeningStatusID    
LEFT OUTER JOIN    
 dbo.InterviewStatus is2 WITH(NOLOCK) on is2.InterviewStatusId=a.T1StatusID     
LEFT OUTER JOIN    
 dbo.InterviewStatus is3 WITH(NOLOCK) on is3.InterviewStatusId=a.T2StatusID     
LEFT OUTER JOIN    
 dbo.InterviewStatus is4 WITH(NOLOCK) on is4.InterviewStatusId=a.HRStatusID     
LEFT OUTER JOIN    
 dbo.InterviewStatus is6 WITH(NOLOCK) on is6.InterviewStatusId=a.WorkingStatusID    
WHERE  
 a.IsDataConsideredForReport=1
GO
/****** Object:  View [dbo].[vwSourcingFormData]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[vwSourcingFormData] AS
SELECT 
    sf.RequisitionID,
    sf.CandidateName,
    sf.Recruiter,
    unp.RoundType,
    unp.DateFilter AS InterviewDate, -- Keep NULL if no data
    unp.Panel AS InterviewPanel,
    ISNULL(ist.InterviewStatus, 'Not Available') AS InterviewStatus
FROM SourcingForm sf

-- Unpivoting the Interview Rounds
CROSS APPLY (
    VALUES 
        ('Screening', sf.ScreeningDateTime, sf.ScreeningPanel, sf.ScreeningStatusID),
        ('T1', sf.T1Date, sf.T1Panel, sf.T1StatusID),
        ('T2', sf.T2Date, sf.T2Panel, sf.T2StatusID),
        ('HR', sf.HRDate, sf.HRPanel, sf.HRStatusID)
) unp(RoundType, DateFilter, Panel, StatusID)

-- Joining with InterviewStatus table to get status names
LEFT JOIN InterviewStatus ist ON unp.StatusID = ist.InterviewStatusID

WHERE sf.IsDeleted = 0  
    AND (unp.DateFilter IS NOT NULL OR unp.StatusID IS NOT NULL);
GO
/****** Object:  View [dbo].[vwGetFeedbackCriteria]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


CREATE View [dbo].[vwGetFeedbackCriteria] 
As 
	Select FeedbackCriteria,IsMandatory from FeedbackCriteria --WITH(NOLOCK)
	WHERE 
    IsMandatory = 1;
	--UNION
	--Select distinct FeedbackCriteria,IsCriteriaMandate from [dbo].FeedbackDetailsCriteria
GO
/****** Object:  View [dbo].[vwGetUserDetails]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
Create View [dbo].[vwGetUserDetails] AS
Select UserRoleMappingID, UserEmail, UserName,a.RoleId,r.RoleName 
from dbo.UserRoleMapping a
inner join dbo.Roles r on r.RoleID=a.RoleId
GO
/****** Object:  View [dbo].[vwGetFeedbackStatus]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

Create View [dbo].[vwGetFeedbackStatus] As
	Select 'Select' FeedbackStatus
	union
	Select 'Reject' FeedbackStatus
	union
	Select 'OnHold' FeedbackStatus
GO
/****** Object:  Table [dbo].[DateMaster]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[DateMaster](
	[Date] [date] NOT NULL,
	[Year] [int] NULL,
	[Quarter] [varchar](50) NULL,
	[Month] [varchar](50) NULL,
	[Day] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[Date] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Employee]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Employee](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[FirstName] [varchar](7) NULL,
	[MiddleName] [varchar](100) NULL,
	[Email] [varchar](255) NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Features]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Features](
	[FeatureID] [int] IDENTITY(1,1) NOT NULL,
	[FeatureName] [varchar](255) NULL,
	[CreatedDate] [datetime] NULL,
	[CreatedBy] [varchar](100) NULL,
	[IsActive] [bit] NULL,
	[IsDropDownMenu] [bit] NULL,
	[RouterLink] [varchar](150) NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[JobDesription_BKP_10162024]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[JobDesription_BKP_10162024](
	[JobDesriptionId] [int] IDENTITY(1,1) NOT NULL,
	[JobTitleId] [varchar](255) NULL,
	[SkillsId] [varchar](100) NULL,
	[JobDesription] [varchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ManpowerRequest]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ManpowerRequest](
	[ID] [tinyint] NULL,
	[Start_time] [datetime2](7) NULL,
	[Completion_time] [datetime2](7) NULL,
	[Email] [nvarchar](255) NULL,
	[Name] [nvarchar](255) NULL,
	[Requestor_Name] [nvarchar](255) NULL,
	[Requirement_raised_for] [nvarchar](255) NULL,
	[Reason_for_Vacancy] [nvarchar](255) NULL,
	[Requisition_ID] [nvarchar](255) NULL,
	[Job_title_based_on_Skill] [nvarchar](255) NULL,
	[Position_Priority] [nvarchar](255) NULL,
	[Designation] [nvarchar](255) NULL,
	[Job_description] [nvarchar](1950) NULL,
	[Location] [nvarchar](255) NULL,
	[Employment_Type] [nvarchar](255) NULL,
	[Reporting_Structure] [nvarchar](255) NULL,
	[Project_Name_Information] [nvarchar](255) NULL,
	[Recruitment_Process] [nvarchar](255) NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Recruiters]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Recruiters](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[RecruiterName] [varchar](100) NULL,
	[isActive] [bit] NOT NULL,
	[createdDate] [datetime] NOT NULL,
	[createdBy] [nvarchar](255) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RoleFeatureMapping]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RoleFeatureMapping](
	[RoleFeatureMappingID] [int] IDENTITY(1,1) NOT NULL,
	[RoleID] [int] NULL,
	[FeatureID] [int] NULL,
	[CreatedDate] [datetime] NULL,
	[CreatedBy] [varchar](100) NULL,
	[IsNavBarEnable] [bit] NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[StgEmployee]    Script Date: 08-04-2025 16:28:26 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[StgEmployee](
	[EmployeeID] [int] IDENTITY(1,1) NOT NULL,
	[FirstName] [varchar](50) NULL,
	[MiddleName] [varchar](100) NULL,
	[Email] [varchar](255) NULL,
	[SurName] [varchar](1000) NOT NULL,
	[IsValidData] [bit] NULL,
	[ErrorDescription] [varchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[Designation] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[Education] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[EmployeeType] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[Features] ADD  DEFAULT ((1)) FOR [IsActive]
GO
ALTER TABLE [dbo].[Features] ADD  DEFAULT ((0)) FOR [IsDropDownMenu]
GO
ALTER TABLE [dbo].[FeedbackCriteria] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[FeedbackCriteria] ADD  DEFAULT ((0)) FOR [IsMandatory]
GO
ALTER TABLE [dbo].[FeedbackDetailsCriteria] ADD  DEFAULT ((0)) FOR [IsCriteriaMandate]
GO
ALTER TABLE [dbo].[FeedbackDetailsCriteria] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[HiringFor] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[InterviewStatus] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[JobDescription] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[OfficialNoticePeriod] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[PointOfContact] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[PositionPriority] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[PreferredLocation] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[Recruiters] ADD  DEFAULT ((1)) FOR [isActive]
GO
ALTER TABLE [dbo].[Recruiters] ADD  DEFAULT (getdate()) FOR [createdDate]
GO
ALTER TABLE [dbo].[Recruiters] ADD  DEFAULT ('system') FOR [createdBy]
GO
ALTER TABLE [dbo].[RecruitmentProcess] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[RequestForm] ADD  DEFAULT ((1)) FOR [IsSendEmailForResponse]
GO
ALTER TABLE [dbo].[RequestForm] ADD  DEFAULT ((0)) FOR [IsActive]
GO
ALTER TABLE [dbo].[RequestForm] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[RequestForm] ADD  DEFAULT ((0)) FOR [IsMigratedData]
GO
ALTER TABLE [dbo].[RequestForm] ADD  DEFAULT ((1)) FOR [IsDataConsideredForReport]
GO
ALTER TABLE [dbo].[RequestRaisedFor] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[RequisitionType] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[Skills] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[SourcingForm] ADD  DEFAULT ((0)) FOR [IsActive]
GO
ALTER TABLE [dbo].[SourcingForm] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[SourcingForm] ADD  DEFAULT ((0)) FOR [IsMigratedData]
GO
ALTER TABLE [dbo].[SourcingForm] ADD  DEFAULT ((1)) FOR [IsDataConsideredForReport]
GO
ALTER TABLE [dbo].[UserRoleMapping] ADD  DEFAULT ('Nandha') FOR [UserName]
GO
ALTER TABLE [dbo].[UserRoleMapping] ADD  DEFAULT ((1)) FOR [IsActive]
GO
ALTER TABLE [dbo].[VacancyReason] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[WorkLocation] ADD  DEFAULT ((0)) FOR [IsDeleted]
GO
ALTER TABLE [dbo].[JobDescription]  WITH CHECK ADD  CONSTRAINT [FK_JobDescription_Designation] FOREIGN KEY([DesignationID])
REFERENCES [dbo].[Designation] ([DesignationID])
GO
ALTER TABLE [dbo].[JobDescription] CHECK CONSTRAINT [FK_JobDescription_Designation]
GO
ALTER TABLE [dbo].[JobDescription]  WITH CHECK ADD  CONSTRAINT [FK_JobDescription_Skills] FOREIGN KEY([SkillsId])
REFERENCES [dbo].[Skills] ([SkillsID])
GO
ALTER TABLE [dbo].[JobDescription] CHECK CONSTRAINT [FK_JobDescription_Skills]
GO

