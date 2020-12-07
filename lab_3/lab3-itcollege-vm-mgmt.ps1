#requires -Version 2 -Modules NetTCPIP
Add-Type -TypeDefinition @"
    public enum Syslog_Facility
    {
        kern,
        user,
        mail,
        daemon,
        auth,
        syslog,
        lpr,
        news,
        uucp,
        clock,
        authpriv,
        ftp,
        ntp,
        logaudit,
        logalert,
        cron,
        local0,
        local1,
        local2,
        local3,
        local4,
        local5,
        local6,
        local7,
    }
"@

Add-Type -TypeDefinition @"
    public enum Syslog_Severity
    {
        Emergency,
        Alert,
        Critical,
        Error,
        Warning,
        Notice,
        Informational,
        Debug
    }
"@

function Send-SyslogMessage
{
    [CMDLetBinding(DefaultParameterSetName = 'RFC5424')]
    Param
    (
        [Parameter(mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [String] 
        $Server,
    
        [Parameter(mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [String]
        $Message,
    
        [Parameter(mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [Syslog_Severity]
        $Severity,
    
        [Parameter(mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [Syslog_Facility] 
        $Facility,
    
        [Parameter(mandatory = $false)]
        [ValidateNotNullOrEmpty()]
        [String]
        $Hostname = 'lab16lnx',
    
        [Parameter(mandatory = $false)]
        [ValidateNotNullOrEmpty()]
        [String]
        $ApplicationName = 'lab3-itcollege-vm-mgmt.ps1',
    
        [Parameter(mandatory = $false, ParameterSetName = 'RFC5424')]
        [ValidateNotNullOrEmpty()]
        [String]
        $ProcessID = $PID,
    
        [Parameter(mandatory = $false, ParameterSetName = 'RFC5424')]
        [ValidateNotNullOrEmpty()]
        [String]
        $MessageID = '-',
    
        [Parameter(mandatory = $false)]
        [ValidateNotNullOrEmpty()]
        [DateTime] 
        $Timestamp = (Get-Date),
    
        [Parameter(mandatory = $false)]
        [ValidateNotNullOrEmpty()]
        [ValidateRange(1,65535)]
        [UInt16]
        $UDPPort = 514
    )

    $Server = "192.168.180.158"

    # Evaluate the facility and severity based on the enum types
    $Facility_Number = $Facility.value__
    $Severity_Number = $Severity.value__
    Write-Verbose -Message "Syslog Facility, $Facility_Number, Severity is $Severity_Number"

    # Calculate the priority
    $Priority = ($Facility_Number * 8) + $Severity_Number
    Write-Verbose -Message "Priority is $Priority"

    <#
            Make sure application name is set
    #>
    if (($ApplicationName -eq '') -or ($ApplicationName -eq $null))
    {
        $ApplicationName = 'lab3-itcollege-vm-mgmt.ps1'
    }

    <#
            Make sure hostname is set
    #>
    if (($Hostname -eq '') -or ($Hostname -eq $null))
    {
        $Hostname = 'lab16lnx'
    }

    #Assemble the full syslog message
    Write-Verbose -Message 'Using RFC 5424 IETF message format'
    #Get the timestamp
    $FormattedTimestamp = $Timestamp.ToString('yyyy-MM-ddTHH:mm:ss.ffffffzzz')
    # Assemble the full syslog formatted Message
    $FullSyslogMessage = '<{0}>1 {1} {2} {3} {4} {5} {6} {7}' -f $Priority, $Hostname, $ApplicationName, $ProcessID, $MessageID, $FormattedTimestamp, $Message

    Write-Verbose -Message "Message to send will be $FullSyslogMessage"

    # create an ASCII Encoding object
    $Encoding = [System.Text.Encoding]::ASCII

    # Convert into byte array representation
    $ByteSyslogMessage = $Encoding.GetBytes($FullSyslogMessage)

    # If the message is too long, shorten it
    if ($ByteSyslogMessage.Length -gt 2048)
    {
        $ByteSyslogMessage = $ByteSyslogMessage.SubString(0, 2048)
    }

    # Create a UDP Client Object
    $UDPCLient = New-Object -TypeName System.Net.Sockets.UdpClient
    $UDPCLient.Connect($Server, $UDPPort)

    # Send the Message
    $null = $UDPCLient.Send($ByteSyslogMessage, $ByteSyslogMessage.Length)

    #Close the connection
    $UDPCLient.Close()
}