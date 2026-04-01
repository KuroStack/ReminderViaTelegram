<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ConversationState extends Model
{
    public $timestamps = false;

    protected $fillable = ['user_id', 'state', 'payload'];

    protected $casts = ['payload' => 'array'];
}
