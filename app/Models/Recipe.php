<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Recipe extends Model
{
    protected $fillable = ['category_id', 'name', 'content'];

    public function category(): BelongsTo
    {
        return $this->belongsTo(RecipeCategory::class, 'category_id');
    }
}
